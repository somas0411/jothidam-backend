"""
manage.py — maintenance commands for the booking database (reads DATABASE_URL).

  python manage.py init-db         create the tables (also done on every start)
  python manage.py seed            add three sample astrologers with obviously fake details
  python manage.py list            list astrologers
  python manage.py add --name "..." --age 52 --phone +919876543210 --email a@b.in --fee 500
  python manage.py deactivate ID   stop taking bookings for an astrologer
  python manage.py purge           wipe personal data past the retention period now
  python manage.py schema          print the PostgreSQL schema (what schema.sql holds)

Astrologers are normally managed on the admin page (admin.html). Their phone
numbers are shown publicly on the astrologer list, so enter only a number the
astrologer has agreed to publish.
"""
import argparse
import sys

from sqlalchemy import insert, select, update
from sqlalchemy.dialects import postgresql
from sqlalchemy.schema import CreateIndex, CreateTable

import booking_core as C
import booking_db as D

SAMPLES = [
    {'name': 'Test Astrologer Arunachalam (Sample)', 'age': 58, 'phone_e164': '+910000000001',
     'email': 'sample.astrologer1@example.com', 'fee_inr': 501, 'languages': 'Tamil, English'},
    {'name': 'Test Astrologer Bhavani (Sample)', 'age': 45, 'phone_e164': '+910000000002',
     'email': 'sample.astrologer2@example.com', 'fee_inr': 351, 'languages': 'Tamil, Telugu'},
    {'name': 'Test Astrologer Chandrasekar (Sample)', 'age': 63, 'phone_e164': '+910000000003',
     'email': 'sample.astrologer3@example.com', 'fee_inr': 1001, 'languages': 'Hindi, English'},
]


def schema_sql():
    dialect = postgresql.dialect()
    parts = [str(CreateTable(t).compile(dialect=dialect)).strip() + ';' for t in D.metadata.sorted_tables]
    for t in D.metadata.sorted_tables:
        parts += [str(CreateIndex(i).compile(dialect=dialect)).strip() + ';' for i in sorted(t.indexes, key=lambda i: i.name)]
    return '\n\n'.join(parts) + '\n'


def seed():
    D.init_db()
    now = D.utcnow()
    added = 0
    with D.engine().begin() as conn:
        for s in SAMPLES:
            if conn.execute(select(D.astrologers.c.id).where(D.astrologers.c.email == s['email'])).first():
                continue
            new_id = conn.execute(insert(D.astrologers).values(created_at=now, updated_at=now, is_active=True, **s)
                                  .returning(D.astrologers.c.id)).scalar_one()
            if s['fee_inr'] == 351:
                # Weekday mornings and Saturday afternoon, to show blocked (grey) slots.
                for weekday in range(5):
                    conn.execute(insert(D.availability).values(astrologer_id=new_id, weekday=weekday,
                                                               start_min=9 * 60, end_min=13 * 60))
                conn.execute(insert(D.availability).values(astrologer_id=new_id, weekday=5,
                                                           start_min=14 * 60, end_min=18 * 60))
            added += 1
    return added


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='cmd', required=True)
    for name in ('init-db', 'seed', 'list', 'purge', 'schema'):
        sub.add_parser(name)
    add = sub.add_parser('add')
    add.add_argument('--name', required=True)
    add.add_argument('--age', type=int, required=True)
    add.add_argument('--phone', required=True)
    add.add_argument('--email', required=True)
    add.add_argument('--fee', type=int, required=True)
    off = sub.add_parser('deactivate')
    off.add_argument('id', type=int)
    args = p.parse_args(argv)

    if args.cmd == 'schema':
        sys.stdout.write(schema_sql())
    elif args.cmd == 'init-db':
        D.init_db()
        print('Tables ready.')
    elif args.cmd == 'seed':
        print(f'Added {seed()} sample astrologer(s).')
    elif args.cmd == 'list':
        with D.engine().connect() as conn:
            for r in conn.execute(select(D.astrologers).order_by(D.astrologers.c.id)):
                print(f'{r.id:4} {"active  " if r.is_active else "inactive"} {r.name} · {r.phone_e164} · ₹{r.fee_inr}')
    elif args.cmd == 'add':
        phone, email = C.clean_phone(args.phone), C.clean_email(args.email)
        if not phone or not email or not 18 <= args.age <= 120 or args.fee < 0:
            sys.exit('Check the phone (E.164, e.g. +919876543210), e-mail, age (18+) and fee.')
        D.init_db()
        now = D.utcnow()
        with D.engine().begin() as conn:
            new_id = conn.execute(insert(D.astrologers).values(
                name=C.clean_text(args.name)[:80], age=args.age, phone_e164=phone, email=email,
                fee_inr=args.fee, is_active=True, created_at=now, updated_at=now)
                .returning(D.astrologers.c.id)).scalar_one()
        print(f'Added astrologer {new_id}.')
    elif args.cmd == 'deactivate':
        with D.engine().begin() as conn:
            conn.execute(update(D.astrologers).where(D.astrologers.c.id == args.id)
                         .values(is_active=False, updated_at=D.utcnow()))
        print(f'Astrologer {args.id} no longer takes bookings.')
    elif args.cmd == 'purge':
        import notify
        print(f'Wiped {notify.purge_personal_data()} booking(s).')


if __name__ == '__main__':
    main()

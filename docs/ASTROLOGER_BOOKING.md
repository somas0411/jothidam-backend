# Astrologer consultations: design, setup and test plan

Visitors pick an astrologer, a 30-minute slot (09:00 to 20:00 IST) and up to
five questions. The booking is e-mailed to the visitor and the astrologer with
the visitor's horoscope PDF and a calendar file. Payment is offline: the
visitor pays the astrologer directly and sends the screenshot on WhatsApp.

Code lives in two repositories:

| Repository | Files |
|---|---|
| **jothidam-backend** | `booking_db.py` (tables), `booking_core.py` (slots, validation, calendar, tokens), `booking_api.py` (routes), `notify.py` (e-mails, outbox, retention), `manage.py` (commands), `schema.sql`, `tests/test_bookings.py`, `.env.example`, this file. `app.py` registers the routes; `requirements.txt` adds SQLAlchemy and psycopg |
| **horoscopegen** | `astrologers.html`, `js/astrologers.js`, `css/astrologers.css`, `admin.html`, `js/admin.js`, `js/config.js` (feature flag). Changed: `index.html` (tab), `js/app.js` (remembers the last birth details in the tab), `js/i18n.js`, `css/main.css`, `sw.js`, `netlify.toml`, `robots.txt`, `privacy.html`, `terms.html`, `README.md` |

## Decisions

**Database: PostgreSQL on Neon's free tier**, reached through `DATABASE_URL`.
Render's disk is wiped on each deploy, so SQLite there would lose bookings.
Neon's free plan is enough for this volume; Supabase works the same way. The
code uses SQLAlchemy Core with psycopg 3, so any PostgreSQL works. The tables
are created on start (`booking_db.init_db`) and are also in `schema.sql`.

**No double bookings, by the database.** A partial unique index on
`(astrologer_id, slot_start_utc) WHERE status = 'confirmed'` makes PostgreSQL
refuse a second confirmed booking for the same slot, however many requests
arrive at once. The API turns that refusal into `409 slot_taken`. A cancelled
booking does not hold its slot. Tested with 8 simultaneous requests: one 201,
seven 409.

**E-mail from an outbox table, sent by a thread in the web process.** A
booking and its two e-mails are written in one transaction. A daemon thread in
the single gunicorn worker sends them within seconds, retries a failure after 1,
4 and 16 minutes (3 attempts), and records each result in
`bookings.notification_status`. This needs no Redis or Celery (not available on
Render's free tier), loses nothing on a restart, and never makes the visitor
wait for the e-mail provider. Rows are claimed with `FOR UPDATE SKIP LOCKED`,
so it stays correct if more workers are added later.

**WhatsApp is click-to-chat, not automatic** (your decision). The confirmation
page has a green button that opens WhatsApp to the astrologer with the
booking, questions and payment note prefilled, and a second button to send the
same to yourself. The visitor sends the payment screenshot in that chat. See
"Adding automatic WhatsApp later" below.

**The horoscope PDF is not stored as a file.** The booking keeps only the
birth details (not the computed chart). The PDF is made with the existing
`generate_pdf()` when the e-mails are sent, and again when the visitor opens
the PDF link. It disappears with the birth details at the retention date.

**The visitor's private link.** Each booking has a token sent only to the
visitor (in the page address and the e-mail). It is derived from
`BOOKING_SECRET`; the database keeps only its SHA-256 hash. Reading,
cancelling, the `.ics` and the PDF all need it. A wrong token and a missing
booking give the same 404.

**Times.** Stored in UTC (`timestamptz`), converted with `zoneinfo` on the
server and `Intl` (timeZone `Asia/Kolkata`) in the browser. A visitor whose
device is in another time zone also sees their own time on every slot.

## API

| Method | Route | |
|---|---|---|
| GET | `/api/astrologers` | active astrologers: id, name, age, phone, fee |
| GET | `/api/astrologers/<id>` | one, with the booking window |
| GET | `/api/astrologers/<id>/slots?date=YYYY-MM-DD` | 22 slots: `available`, `booked`, `blocked` or `past` |
| POST | `/api/bookings` | 201 with the booking and its token; 409 `slot_taken` / `slot_unavailable` / `astrologer_unavailable`; 422 with `fields`; 429 |
| GET | `/api/bookings/<id>?token=` | the booking |
| POST | `/api/bookings/<id>/cancel` | body `{"token"}`; frees the slot, e-mails both |
| GET | `/api/bookings/<id>/ics?token=` | calendar file, reminders 1 day and 30 min before |
| GET | `/api/bookings/<id>/pdf?token=` | the horoscope PDF |
| | `/api/admin/...` | header `X-Admin-Key`; see the docstring of `booking_api.py` |

Errors are `{"error", "code", "fields"}`. Limits per visitor: booking 5 an
hour, cancel 10 an hour, slots and lists 60 a minute. A hidden honeypot field
turns away form-filling bots. An `idempotency_key` sent with the booking makes a
repeated click return the same booking instead of a second one.

## Setup

### 1. Database (Neon, free)

1. Sign up at neon.tech and create a project in the **AWS Asia Pacific (Singapore)** region (closest to Render's Singapore region and to India).
2. Copy the connection string (it ends with `?sslmode=require`).
3. Optional: run `psql "<connection string>" -f schema.sql`. The app also creates the tables on its first start.
4. Optional, to try it out: `DATABASE_URL="<connection string>" python manage.py seed` adds three sample astrologers named "Test Astrologer … (Sample)" with phone numbers `+91000000000x`. Deactivate them before going live (admin page, or `python manage.py deactivate ID`).

Neon pauses an idle database after 5 minutes; the first request after that takes about a second longer. The app's connection pool checks connections before use, so this needs nothing else.

### 2. E-mail (Brevo, free 300 a day)

1. Sign up at brevo.com. Under **Senders, Domains & Dedicated IPs → Domains**, add `horoscopegen.in`.
2. Brevo shows DNS records to add where the domain's DNS is managed (your registrar, or Netlify DNS if the domain uses it). Copy the exact values Brevo shows; they look like:

   | Type | Name | Value |
   |---|---|---|
   | TXT | `@` | `brevo-code:…` (ownership) |
   | CNAME | `brevo1._domainkey` | `b1.horoscopegen-in.dkim.brevo.com` (DKIM) |
   | CNAME | `brevo2._domainkey` | `b2.horoscopegen-in.dkim.brevo.com` (DKIM) |
   | TXT | `@` | `v=spf1 include:spf.brevo.com ~all` (SPF) |
   | TXT | `_dmarc` | `v=DMARC1; p=none; rua=mailto:<your address>` |

   A domain may have only **one** SPF record. If `horoscopegen.in` already has one (for example for Google Workspace or Zoho mail), add `include:spf.brevo.com` to it instead of adding a second.
3. Press **Authenticate** in Brevo once the records are live (minutes to a few hours).
4. Add a sender `bookings@horoscopegen.in` (it need not be a real mailbox; replies go to the astrologer or the visitor through Reply-To).
5. Create an API key under **SMTP & API → API keys**.

Any SMTP server works instead: set `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD` and leave `BREVO_API_KEY` empty.

### 3. Backend (Render)

In the service's **Environment**, add (see `.env.example`):

```
DATABASE_URL     = <Neon connection string>
BOOKING_SECRET   = <python -c "import secrets; print(secrets.token_hex(32))">
ADMIN_API_KEY    = <another long random string; you type it on admin.html>
BREVO_API_KEY    = <from Brevo>
EMAIL_FROM       = HoroscopeGen <bookings@horoscopegen.in>
SITE_URL         = https://horoscopegen.in
PUBLIC_API_URL   = https://jothidam-backend.onrender.com
```

Deploy. The build command (`pip install -r requirements.txt`) picks up the two
new packages. Check `https://jothidam-backend.onrender.com/api/astrologers`
answers `{"astrologers": [...]}` rather than a 503.

A free Render service sleeps after 15 minutes without traffic. E-mails go out
within seconds of a booking, while the server is awake; a retry that falls due
while it sleeps runs at the next wake-up.

### 4. Website (Netlify)

Nothing to configure: the site already reads the backend address from
`js/app.js`, and `netlify.toml` holds the `/astrologers`, `/astrologers/book`
and `/admin` routes. Deploy the `horoscopegen` branch.

### 5. Add astrologers

Open `https://horoscopegen.in/admin`, enter `ADMIN_API_KEY`, press **Add
astrologer**. Tick **Set weekly hours** and click or drag over the half-hours
when they are available (green); leave it unticked for 09:00–20:00 every day.
Add **Days off** for leave. Visitors see booked slots in red automatically.

The phone number is shown publicly on the astrologer list, by design: enter only
a number the astrologer agrees to publish. The e-mail is never shown.

### 6. Go live

In `horoscopegen/js/config.js`, change

```js
ASTROLOGERS_NAV_ENABLED: false,
```

to `true` and deploy. The tab on the home page becomes active and drops the
"Coming Soon" caption. When you want the page in search results, also remove
the `noindex` meta tag in `astrologers.html`, the `X-Robots-Tag` header for
`/astrologers*` in `netlify.toml`, `Disallow: /astrologers` in `robots.txt`,
and add the page to `sitemap.xml`. Keep `/admin` hidden.

## Adding automatic WhatsApp later

To have the server message the astrologer itself, use the WhatsApp Business
Cloud API (Meta). It needs a Meta Business account, a phone number not already
on WhatsApp, and pre-approved templates (category **UTILITY**). Meta charges per
conversation. Templates to submit:

| Name | Header | Body |
|---|---|---|
| `booking_confirmed_astrologer` | Document (the horoscope PDF) | `New consultation booked: {{1}} on {{2}} IST. Client: {{3}}, WhatsApp {{4}}. Booking ID {{5}}. Questions are in the e-mail and the PDF. Payment screenshot expected from the client before the session; please confirm receipt to them.` |
| `booking_cancelled_astrologer` | none | `The consultation with {{1}} on {{2}} IST (Booking ID {{3}}) has been cancelled. The slot is free again.` |
| `booking_confirmed_user` (optional) | Document | `Your consultation with {{1}} is booked for {{2}} IST. Booking ID {{3}}. Pay ₹{{4}} to the astrologer directly and send the payment screenshot to {{5}} on WhatsApp before the session.` |

In code, this is a second channel in `notify.enqueue()` and a `send_whatsapp()`
next to `send_email()`, with `WHATSAPP_TOKEN`, `WHATSAPP_PHONE_NUMBER_ID` and
`WHATSAPP_TEMPLATE_*` settings; the outbox, retries and status already handle
any channel.

## Manual test plan

Do this on a Netlify deploy preview or the live site with the flag still off.

1. **Coming Soon tab.** Open the home page. The 🔮 Astrologers tab is grey, says "Coming Soon", and nothing happens on click or Enter. The Horoscope and Marriage tabs work as before.
2. **Direct address.** Open `/astrologers`, `/astrologers.html` and `/astrologers/book?id=1`: the list, the list, and the booking form for astrologer 1. View the page source: `noindex,nofollow` is there.
3. **Cold start.** After the backend has slept (15 min), open `/astrologers`: "Waking up server…" appears, then the list.
4. **Phone layout.** On a phone (or browser width 360px), the table turns into cards with a full-width Book button; the date strip scrolls sideways; the slot grid has 3–4 columns.
5. **Full booking.** Generate a horoscope on the home page first, then book: pick tomorrow, a green slot, write Q1 in Tamil with an emoji, fill your own e-mail and WhatsApp, tick the three boxes. The button stays disabled and lists what is missing until all is filled. Book. The confirmation page shows the booking ID; within a minute it says the e-mails were sent. Check both inboxes: subject "Appointment confirmed…", questions numbered, the payment steps with the fee, the horoscope PDF and the `.ics` attached, the Tamil text intact in the PDF.
6. **WhatsApp.** Press the green WhatsApp button: WhatsApp opens to the astrologer's number with the booking and questions filled in.
7. **Calendar.** "Add to Google Calendar" opens Google Calendar at the right IST time with the booking ID in the details. "Download .ics" opens in Apple Calendar / Outlook with a reminder.
8. **Red slot.** In another browser, open the same astrologer and date: the slot is red and says "Booked".
9. **Double booking.** Open the same free slot in two browsers, fill both forms, press Book in both. One gets the confirmation; the other gets "Sorry, that slot was just taken" and the slot turns red.
10. **Cancel.** On the confirmation page, press "Cancel booking". Both receive a cancellation e-mail; the slot is green again for others.
11. **Admin.** On `/admin`, set an astrologer to Tuesday 10:00–12:00 only: the booking page shows only those four slots green on Tuesdays. Add a day off: that day is all grey. Untick Active: the astrologer leaves the list, and a booking form left open shows "no longer taking bookings" on submit.
12. **Language.** Switch to தமிழ் on the booking page: labels, payment steps and slot legend change; entered text stays.

## Retention and deletion

`notify.purge_personal_data()` runs every hour in the worker and wipes the
name, e-mail, WhatsApp number, birth details and questions of bookings whose
appointment ended more than `RETENTION_DAYS` (90) days ago. For a deletion
request: `python manage.py forget <booking id>` (wipes now, cancels if still
upcoming). The privacy policy describes both.

## Assumptions and open questions

1. **Retention 90 days** after the appointment. Shorter is fine for privacy; longer helps if an astrologer asks about an old booking.
2. **Lead time 2 hours, window 30 days, 5 bookings per hour per visitor.** All are settings.
3. **Astrologer e-mails are in English**; the visitor's e-mail is in the language they booked in (English or Tamil today; other languages fall back to English).
4. **Cancellation** is allowed until the slot starts. There is no rule about refunds; the terms say that is between the visitor and the astrologer.
5. **Blocking a day does not cancel existing bookings on it.** Cancel them from the admin bookings list (both get an e-mail).
6. **The admin key is one shared key.** Fine for one owner. An astrologer login portal (their own bookings and hours only) is a v2 item.
7. **Rate limits are per server process** (as for the rest of the API). Correctness of bookings does not depend on them.
8. **Future work, designed for but not built:** automatic WhatsApp (above), an astrologer "mark as paid", online payment, astrologer logins, video-call links, reviews, SMS.

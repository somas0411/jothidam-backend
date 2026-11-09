# Paid reports, support tickets and the AI switch

## What is live as soon as this is deployed

| Change | Effect |
|---|---|
| `AI_TABS_ENABLED` (default **false**) | No `AI_` sheet in any workbook (horoscope, marriage, family). The Notes sheet (குறிப்புகள்) has no "AI sheets" section. The marriage sheet no longer points to `AI_MatchWindows`. `/api/download/json` answers 404, and `"ai": true` / `"ai": "brief"` are ignored. Set it to `true` to bring all of this back. `enrich.py` is kept, because the Predictions sheet is built from it. |
| Predictions sheet (பலன்கள்) | The "Chart basis" column (ஜாதக அடிப்படை and its 7 translations) is removed. The readings are unchanged. |
| Support tickets | `POST /api/tickets` (needs `DATABASE_URL`). Tickets are e-mailed to `SUPPORT_EMAIL` and acknowledged to the visitor. Admin: `GET/PUT /api/admin/tickets`. |
| Payments | Built but **off**. Every download stays free, as before. |

## Products (INR only)

| Code | Price (env) | Contents |
|---|---|---|
| `basic` | `PRICE_BASIC_PAISE` = 20000 (₹200) | Summary, Vedic, KP, ALP, Dasa (PDF + Excel) |
| `full` | `PRICE_FULL_PAISE` = 50000 (₹500) | basic + divisional charts + Notes (குறிப்புகள்) + Predictions (பலன்கள், with KP timing) |
| `match` | `PRICE_MATCH_PAISE` = 20000 (₹200) | Marriage matching report |
| `family` | `PRICE_FAMILY_PAISE` = 50000 (₹500) | Family reading report |

Viewing the horoscope on the website stays free. With payments on, the Predictions tab on the page is shown locked (`predictions_locked: true`), because பலன்கள் is part of the ₹500 product.

## Routes

| Route | |
|---|---|
| `GET /api/options` | adds `payments_enabled`, `currency`, `products` [{code, price_paise, name, includes}] (`?lang=ta` for names) |
| `POST /api/orders` | `{product, email, phone?, lang, consent: true, request: {the body the free route would get}}` → 201 `{order_id, razorpay_order_id, key_id, amount, currency, prefill}` |
| `POST /api/orders/<id>/verify` | Checkout's `{razorpay_order_id, razorpay_payment_id, razorpay_signature}` → `{status: paid, token, links}` |
| `GET /api/orders/<id>?token=` | status for the success page |
| `GET /api/orders/<id>/download/pdf|excel?token=` | the paid files, for `PAYMENT_LINK_HOURS` after payment |
| `POST /api/payments/webhook` | Razorpay → us. Events: `payment.captured`, `order.paid`, `payment.failed`, `refund.processed` |

With payments on, the six free download routes answer **402**.

## Go-live checklist

1. LLP registered, current account opened, Razorpay KYC approved. Razorpay checks the website: terms, privacy, refund, delivery and contact pages must be live (in the horoscopegen repo: fill in the `{{LLP_NAME}}`, `{{LLP_ADDRESS}}`, `{{GSTIN_IF_ANY}}` placeholders first).
2. On Render (env group "Horoscope"), set `RAZORPAY_KEY_ID` / `RAZORPAY_KEY_SECRET` (the **test** keys first), `RAZORPAY_WEBHOOK_SECRET`, `PAYMENT_SECRET` and `SUPPORT_EMAIL`. Leave `PAYMENTS_ENABLED=false`.
3. In the Razorpay dashboard → Webhooks, add `https://jothidam-backend.onrender.com/api/payments/webhook` with the same secret and the four events above.
4. Test on a Netlify deploy preview (add its URL to `EXTRA_ORIGINS`) with `PAYMENTS_ENABLED=true` and the test keys: buy each of the 4 products, download both files, close the browser during a payment (the webhook should still mark it paid), refund one.
5. Swap to the live keys, redeploy, buy one real ₹200 report, and refund it.

## Not verified in development

Real Razorpay calls (mocked in `tests/test_payments.py`), webhooks sent by Razorpay's servers, e-mail delivery through Resend, and production CSP on Netlify.

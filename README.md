# Lendly

Campus rental marketplace — Airbnb for items, scoped to .edu communities.

Django 5 + PostgreSQL + Stripe + Google Vision + eBay API, served with Tailwind CSS and vanilla JS templates.

## Features

- **.edu-only signup** with email verification (allauth + custom adapter)
- **Listings** with multiple images, categories, conditions, per-day pricing, and deposits
- **AI price suggestion** — Google Vision labels → eBay sold-price lookup → rental rate
- **Browse** with search, category/campus filters, price range, sorting, pagination
- **Booking flow** — request → owner approves/denies → Stripe Checkout → paid
- **Stripe webhook** updates booking + payment status on `checkout.session.completed`
- **Messaging** — threads per listing with AJAX send and 3s polling refresh
- **Reviews** after completed bookings
- **Dashboard** — earnings, my listings, my rentals, incoming requests
- **Django admin** configured for all models

## Project structure

```
lendly/
├── lendly/            # project config
├── users/             # custom User, Campus, .edu adapter
├── listings/          # listings, categories, AI pricing
├── bookings/          # rental requests, approval flow
├── messaging/         # conversations, messages, polling
├── reviews/           # post-booking reviews
├── payments/          # Stripe checkout + webhook
├── templates/         # all HTML templates
├── static/            # css + js
└── media/             # uploaded images (local dev)
```

## Local setup

```bash
cp .env.example .env
# edit .env with your Stripe test keys etc.

docker compose up --build
# wait for migrations to run, then:
docker compose exec web python manage.py createsuperuser
docker compose exec web python manage.py seed
```

Open http://localhost:8000.

Seeded demo login: `demo@cpp.edu` / `demopass123`.

## Without Docker

```bash
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
createdb lendly
cp .env.example .env
python manage.py migrate
python manage.py seed
python manage.py runserver
```

## Stripe webhook (local)

```bash
stripe listen --forward-to localhost:8000/payments/webhook/
```

Copy the `whsec_...` it prints into `STRIPE_WEBHOOK_SECRET` in `.env`.

## AI price suggestion

Requires:
- `GOOGLE_APPLICATION_CREDENTIALS` pointing to a service account JSON with Vision API enabled
- `EBAY_APP_ID` from the eBay developer program

If either is missing, the "Suggest" button returns a graceful 502 and the rest of the app still works.

## Tests

```bash
python manage.py test
```

6 tests covering user model, .edu adapter, listing slug/browse/detail, and booking total computation.

## Key models

- `users.User` — custom, email-as-username, linked to a `Campus`
- `users.Campus` — name, slug, email_domain (gates signup)
- `listings.Listing` — owner, campus, category, condition, price, AI-suggested price
- `listings.ListingImage` — multiple per listing
- `bookings.Booking` — renter, dates, status state machine, computed total
- `messaging.Conversation` + `Message` — M2M participants, polling endpoint
- `reviews.Review` — 1-5 stars tied to completed bookings
- `payments.Payment` — Stripe session + intent, status

## Notes

Media files go to local `/media` by default. Set `USE_S3=True` and fill the AWS vars to switch to S3.

Static files are served by WhiteNoise in production.

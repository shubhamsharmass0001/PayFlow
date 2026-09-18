# PayFlow Monorepo

PayFlow is a full-stack payments and UPI transaction platform. This repository contains the complete monorepo skeleton organized into backend services, a Flutter mobile client, container orchestration, and documentation.

> [!NOTE]
> This repository contains architecture, boilerplate, and foundational scaffolding. No business logic has been implemented yet.

---

## Directory Structure

```text
.
├── backend/            # FastAPI backend service
│   ├── alembic/        # Database migrations (Alembic)
│   ├── alembic.ini     # Alembic configuration
│   ├── app/
│   │   ├── core/       # Config (pydantic-settings), security, logging, middleware, Celery
│   │   ├── db/         # SQLAlchemy Base & SessionLocal engine
│   │   ├── modules/    # 23 functional module packages (auth, payments, upi_qr, etc.)
│   │   ├── shared/     # Pagination, custom exceptions, idempotency helpers
│   │   └── main.py     # FastAPI application entrypoint & Swagger UI (/docs)
│   ├── Dockerfile      # Python 3.11 container image
│   └── requirements.txt# Backend Python dependencies
├── mobile/             # Flutter mobile application (Dart 3.x, null-safety)
│   ├── lib/
│   │   ├── core/       # ApiClient (Dio with JWT & auto-refresh on 401), Config
│   │   ├── features/   # 23 feature packages mirroring backend modules
│   │   ├── models/     # Freezed & json_serializable typed API models
│   │   ├── routing/    # GoRouter navigation configuration
│   │   ├── state/      # Riverpod state management & auth providers
│   │   └── main.dart   # App entry point wrapped in ProviderScope
│   └── pubspec.yaml    # Flutter dependencies
├── docker/             # Container orchestration
│   └── docker-compose.yml # PostgreSQL 16, Redis 7, FastAPI backend, Celery worker & beat
├── docs/               # System documentation
│   ├── architecture.md # System architecture documentation placeholder
│   ├── db-schema.md    # Database schema specification placeholder
│   └── api-spec.md     # OpenAPI / REST endpoint specification placeholder
├── .env.example        # Environment variable template
└── README.md           # Getting started and setup guide
```

---

## 1. Backend Stack Setup (Docker)

The backend stack includes:
- **PostgreSQL 16**: Primary relational database
- **Redis 7**: Cache layer and Celery message broker/result backend
- **Backend (FastAPI)**: Hot-reloading API service on port `8000`
- **Celery Worker**: Background task consumer
- **Celery Beat**: Periodic task scheduler

### Getting Started

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Start all services using Docker Compose:
   ```bash
   docker compose -f docker/docker-compose.yml up --build
   ```

3. Access the interactive API documentation (Swagger UI):
   - **Swagger UI**: [http://localhost:8000/docs](http://localhost:8000/docs)
   - **ReDoc**: [http://localhost:8000/redoc](http://localhost:8000/redoc)
   - **Health Check**: [http://localhost:8000/health](http://localhost:8000/health)

---

## 2. Mobile App Setup (Flutter)

The mobile application is located in `/mobile` and runs directly via the Flutter toolchain against the dockerized backend.

### Prerequisites
- Flutter SDK (>= 3.13.x / Dart 3.x)
- Android Studio / Xcode (for simulators or device deployment)

### Installing Dependencies
```bash
cd mobile
flutter pub get
```

### Pointing Mobile App at the Backend

When connecting from the mobile app to the backend running inside Docker on your host machine, the network address depends on your execution target:

| Target Platform | Target URL | Explanation |
| :--- | :--- | :--- |
| **Android Emulator** | `http://10.0.2.2:8000` | The Android emulator runs in a separate network namespace; `10.0.2.2` routes directly to host `localhost`. |
| **iOS Simulator** | `http://localhost:8000` | iOS Simulator shares the macOS host network stack directly. |
| **Physical Device (Android / iOS)** | `http://<YOUR_LAN_IP>:8000` | A physical device on the same Wi-Fi / Local Area Network connects via your development machine's local IP (e.g. `http://192.168.1.100:8000`). |

#### How to Find Your LAN IP
- **macOS**: `ipconfig getifaddr en0` (or `ipconfig getifaddr en1`)
- **Linux**: `hostname -I | awk '{print $1}'`
- **Windows**: `ipconfig` (look for IPv4 Address)

#### Running with Custom Base URL
Pass the backend base URL via `--dart-define=BASE_URL=...` when launching Flutter:

```bash
# Android Emulator (Default if not specified)
flutter run -d emulator --dart-define=BASE_URL=http://10.0.2.2:8000

# iOS Simulator
flutter run -d "iPhone 15" --dart-define=BASE_URL=http://localhost:8000

# Physical Device on Local Wi-Fi
flutter run -d <DEVICE_ID> --dart-define=BASE_URL=http://192.168.1.100:8000
```

> [!TIP]
> The mobile client's [`AppConfig`](file:///Users/shubhamsharma/Desktop/transaction/mobile/lib/core/config.dart) automatically defaults to `http://10.0.2.2:8000` on Android and `http://localhost:8000` on iOS/desktop if `--dart-define=BASE_URL` is omitted.

---

## 3. Architecture & Code Generation

### Mobile Code Generation
When updating models with `@freezed` and `@JsonSerializable`:
```bash
cd mobile
dart run build_runner build --delete-conflicting-outputs
```

### Database Migrations
When adding new SQLAlchemy models to `app/modules/`:
```bash
cd backend
alembic revision --autogenerate -m "description_of_migration"
alembic upgrade head
```

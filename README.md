# 🛡️ CampusSentinel

**CampusSentinel** is an enterprise-grade, centralized lab activity monitoring, network access tracking, and endpoint telemetry platform tailored for educational institutions, university computer labs, schools, and academic research facilities.

The platform bridges IT management, ethical device telemetry, and lab inventory tracking into a unified ecosystem. It combines an **ethical, user-transparent background client agent**, a high-performance **FastAPI backend API**, and a modern **React administrative console** to give campus administrators real-time visibility into computer lab operations.

---

## 📑 Table of Contents

- [Core Features](#-core-features)
- [Ethical & Transparent Telemetry Philosophy](#-ethical--transparent-telemetry-philosophy)
- [System Architecture](#-system-architecture)
- [How It Works](#-how-it-works)
  - [1. Device Registration & Enrollment](#1-device-registration--enrollment)
  - [2. Periodic Telemetry & Heartbeat Loop](#2-periodic-telemetry--heartbeat-loop)
  - [3. Real-Time Admin Monitoring & Inspection](#3-real-time-admin-monitoring--inspection)
- [Repository Structure](#-repository-structure)
- [Technology Stack](#-technology-stack)
- [Database Schema & Data Models](#-database-schema--data-models)
- [REST API Reference](#-rest-api-reference)
- [Prerequisites](#-prerequisites)
- [Getting Started & Installation](#-getting-started--installation)
  - [Step 1: Database Setup (Docker)](#step-1-database-setup-docker)
  - [Step 2: Backend API Setup](#step-2-backend-api-setup)
  - [Step 3: Frontend Web Console Setup](#step-3-frontend-web-console-setup)
  - [Step 4: Endpoint Agent Setup](#step-4-endpoint-agent-setup)
- [Running Automated Tests](#-running-automated-tests)
- [Environment Configuration](#-environment-configuration)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## ✨ Core Features

- 🖥️ **Centralized Lab & Device Inventory**:
  - Partition devices by physical laboratory rooms (e.g., *Computer Lab A*, *Robotics Lab*).
  - Track computer hostnames, unique hardware/system identifiers (`device_uid`), IP addresses, MAC addresses, and assignment status (`active`, `inactive`, `quarantined`).

- 💓 **Real-Time Heartbeat & Liveness Tracking**:
  - Continuous endpoint status monitoring with customizable reporting intervals.
  - Automatic online/offline state computation in the UI (active green indicator if heartbeat received within 90 seconds, red indicator when disconnected).

- 📊 **Process & Application Inspection**:
  - Endpoint telemetry agent detects foreground desktop applications and background processes using native system calls (`psutil`).
  - Stores timestamped snapshots for remote administrative diagnostic inspection.

- 📜 **Full Lifecycle Audit Timeline**:
  - Automatically records state transitions: Initial Enrollment (`enrolled`), Re-discovery/Check-in (`re_seen`), and Status Changes (`status_changed`).
  - Historical query support for security investigations and forensics.

- 🔍 **Interactive Admin Console**:
  - Live search and instant filtering across labs, hostnames, device IDs, and statuses.
  - Auto-refreshes device telemetry every 30 seconds.
  - Interactive Master-Detail slide-out drawer revealing live process lists, application snapshots, and historical events.

- 🤝 **User Disclosure & Transparency by Design**:
  - Student and lab-user awareness dialog on agent startup.
  - Permanent system tray presence allowing users to right-click and inspect exactly what telemetry data is being reported back to administration.

---

## 🔒 Ethical & Transparent Telemetry Philosophy

Unlike invasive spyware or covert keyloggers, **CampusSentinel** is built around ethical observability:

1. **Disclosure on Launch**: When the agent starts up, it presents a graphical modal informing the user that the machine is an institution-managed workstation subject to lab usage policies.
2. **System Tray Visibility**: An active system tray icon ensures that telemetry collection is never hidden from the user.
3. **Data Inspection for Users**: Any student or operator can right-click the tray icon and select **"View what's reported"** to see the exact count of applications and processes transmitted in the latest snapshot.
4. **Focused Scope**: Only process executable metadata is captured; keystrokes, personal screen recordings, webcam feeds, and browser history are strictly excluded.

---

## 🏗️ System Architecture

CampusSentinel operates on a 3-tier distributed architecture:

```mermaid
flowchart TD
    subgraph Client Workstations ["Monitored Lab Workstations"]
        Agent["CampusSentinel Python Agent\n(psutil + pystray + tkinter)"]
        UserNotice["Transparency Notice\n& System Tray UI"]
        Agent --> UserNotice
    end

    subgraph Central Server ["Central Infrastructure"]
        subgraph Backend ["FastAPI Application (Port 8000)"]
            AgentRouter["/api/v1/agent\n(Heartbeat & Telemetry)"]
            DeviceRouter["/api/v1/devices\n(Enrollment & Inventory)"]
            AdminRouter["/api/v1/admin\n(Dashboard Feeds & Snapshots)"]
            LabRouter["/api/v1/labs\n(Lab Grouping)"]
        end

        subgraph Database ["PostgreSQL 16 (Docker Port 5432)"]
            LabsTable[("labs")]
            DevicesTable[("devices")]
            EventsTable[("device_events")]
            SnapshotsTable[("device_snapshots")]
        end
    end

    subgraph Admin Web App ["Administrative Console (Vite + React, Port 5173)"]
        RegPage["Device Registration Page (/)"]
        DashPage["Live Admin Dashboard (/admin)"]
    end

    %% Communications
    Agent -- "1. POST /api/v1/agent/heartbeat\n(x-device-uid + snapshot)" --> AgentRouter
    RegPage -- "2. POST /api/v1/devices/enroll" --> DeviceRouter
    DashPage -- "3. GET /api/v1/admin/* (Polling & Inspection)" --> AdminRouter

    Backend --> LabsTable
    Backend --> DevicesTable
    Backend --> EventsTable
    Backend --> SnapshotsTable
```

---

## ⚙️ How It Works

### 1. Device Registration & Enrollment
1. An administrator or lab technician navigates to the registration portal at `http://127.0.0.1:5173/`.
2. The technician selects the designated lab from a dynamically loaded dropdown, enters the PC Number (e.g., `101`), device hostname, and optional MAC address.
3. The frontend submits a registration request to `POST /api/v1/devices/enroll`.
4. The backend:
   - Formats or validates the device UID (`PC-101`).
   - Automatically detects and records the client's connecting IP address.
   - Creates a database record in `devices` with status `active`.
   - Records an initial lifecycle event `enrolled` in `device_events`.

### 2. Periodic Telemetry & Heartbeat Loop
1. The **CampusSentinel Agent** starts on the lab machine (configured with its `DEVICE_UID`, e.g., `PC-101`).
2. The agent displays an acknowledgment dialog notifying the student/user of monitoring.
3. A background daemon thread triggers every `INTERVAL_SECONDS` (default: 60s):
   - Scans active processes using `psutil`.
   - Distinguishes desktop executable applications from system processes (excluding Windows internals such as `svchost.exe`, `conhost.exe`).
   - Deduplicates and structures the telemetry payload into:
     ```json
     {
       "applications": ["chrome.exe", "code.exe", "matlab.exe"],
       "processes": ["explorer.exe", "code.exe", "..."]
     }
     ```
   - Sends a signed HTTP POST request with header `x-device-uid: PC-101` to `POST /api/v1/agent/heartbeat`.
4. The backend verifies device authorization, updates `last_seen_at` to the current UTC timestamp, and appends a `DeviceSnapshot` JSON record.

### 3. Real-Time Admin Monitoring & Inspection
1. The administrator visits the dashboard at `http://127.0.0.1:5173/admin`.
2. The dashboard automatically queries `GET /api/v1/admin/devices` every 30 seconds.
3. If a device has checked in within the last 90 seconds, a **green status indicator** is displayed; otherwise, a **red offline indicator** appears.
4. Clicking any device row opens the inspection drawer:
   - Fetches the latest process snapshot via `GET /api/v1/admin/devices/{uid}/snapshot`.
   - Fetches the event audit log via `GET /api/v1/admin/devices/{uid}/history`.
   - Lists active applications, top background processes, and enrollment timeline.

---

## 📁 Repository Structure

```text
CampusSentinel/
├── docker-compose.yml              # PostgreSQL 16 container definition
├── README.md                       # Comprehensive project documentation
│
├── agent/                          # Desktop client agent for lab machines
│   ├── agent.py                    # Main agent daemon (telemetry collector & heartbeat loop)
│   ├── config.py                   # Environment loader (UID, backend URL, interval)
│   ├── notice.py                   # First-run / startup disclosure modal (Tkinter)
│   ├── tray.py                     # Interactive system tray app (Pystray + Pillow)
│   ├── requirements.txt            # Python dependencies for the agent
│   └── README.md                   # Agent setup and configuration guide
│
├── backend/                        # Central FastAPI management service
│   ├── alembic/                    # Database schema migrations
│   │   ├── env.py                  # Alembic environment runner
│   │   └── versions/               # Migration script history
│   │       ├── 4530abcf0eba_add_lab_and_device_tables.py
│   │       ├── 5d15a722bbae_add_device_events.py
│   │       └── d6d5582900d7_add_device_snapshots.py
│   ├── app/
│   │   ├── main.py                 # FastAPI initialization, CORS middleware, router registration
│   │   ├── core/
│   │   │   └── config.py           # Pydantic BaseSettings configuration loader
│   │   ├── db/
│   │   │   ├── base.py             # SQLAlchemy DeclarativeBase
│   │   │   └── session.py          # SessionLocal database factory and dependency
│   │   ├── models/                 # SQLAlchemy ORM models
│   │   │   ├── lab.py              # Lab model
│   │   │   ├── device.py           # Device model & DeviceStatus enum
│   │   │   ├── device_event.py     # DeviceEvent model & EventType enum
│   │   │   └── device_snapshot.py  # DeviceSnapshot telemetry model
│   │   ├── schemas/                # Pydantic validation & serialization models
│   │   │   ├── lab.py              # LabCreate, LabRead schemas
│   │   │   ├── device.py           # DeviceEnroll, DeviceRead, DeviceAdminRead schemas
│   │   │   └── device_snapshot.py  # DeviceSnapshotCreate, DeviceSnapshotRead schemas
│   │   └── api/v1/                 # Versioned API routes
│   │       ├── admin.py            # Admin device list, event history, process snapshots
│   │       ├── agent.py            # Agent heartbeat receiver endpoint
│   │       ├── devices.py          # Device enrollment and query endpoints
│   │       └── labs.py             # Lab creation and listing endpoints
│   ├── tests/                      # Pytest automated test suite
│   │   ├── conftest.py             # SQLite in-memory fixtures & mock database session
│   │   ├── test_admin.py           # Tests for admin device and history endpoints
│   │   ├── test_admin_snapshots.py # Tests for telemetry snapshot retrieval
│   │   ├── test_agent_heartbeat.py # Tests for agent heartbeat submission
│   │   ├── test_devices.py         # Tests for device registration and filtering
│   │   ├── test_labs.py            # Tests for lab creation and uniqueness
│   │   └── test_main.py            # Tests for health check endpoint
│   ├── alembic.ini                 # Alembic configuration
│   ├── pytest.ini                  # Pytest configuration
│   ├── requirements.txt            # Backend Python dependencies
│   └── .env.example                # Template for backend environment variables
│
└── frontend/                       # React 18 single-page application
    ├── index.html                  # HTML entry point
    ├── vite.config.js              # Vite configuration & Vitest jsdom setup
    ├── package.json                # Frontend dependencies & scripts
    ├── .env.example                # Template for frontend environment variables
    └── src/
        ├── main.jsx                # React root mount
        ├── App.jsx                 # Navigation header and route declarations
        ├── api/
        │   ├── client.js           # API client for lab fetching and device enrollment
        │   └── adminClient.js      # API client for admin dashboard telemetry and history
        └── pages/
            ├── RegisterDevice.jsx       # Workstation enrollment form page
            ├── RegisterDevice.test.jsx  # Unit & integration tests for registration form
            ├── AdminDashboard.jsx       # Real-time monitoring dashboard with inspection drawer
            └── AdminDashboard.test.jsx  # Tests for dashboard rendering and interaction
```

---

## 💻 Technology Stack

| Layer | Technology | Description |
|---|---|---|
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) (Python 3.10+) | High-performance asynchronous REST API framework |
| **ORM & Database** | [SQLAlchemy 2.0](https://www.sqlalchemy.org/) + [PostgreSQL 16](https://www.postgresql.org/) | Type-safe ORM with async-ready architecture and relational persistence |
| **Schema Migrations** | [Alembic](https://alembic.sqlalchemy.org/) | Automated database versioning and migration management |
| **Data Validation** | [Pydantic v2](https://docs.pydantic.dev/) | Strict payload typing, environment loading, and serialization |
| **Desktop Agent** | Python (`psutil`, `pystray`, `Pillow`, `tkinter`) | Low-overhead system process auditor, system tray controller, and disclosure UI |
| **Frontend Framework** | [React 18](https://react.dev/) + [Vite](https://vitejs.dev/) | Modern reactive web UI with fast HMR |
| **Routing** | [React Router v7](https://reactrouter.com/) | Client-side routing between registration and admin consoles |
| **Containerization** | [Docker Compose](https://docs.docker.com/compose/) | Isolated local PostgreSQL development instance |
| **Testing** | `pytest` + `httpx` (Backend) / `Vitest` + `Testing Library` (Frontend) | Full-stack unit and integration test coverage |

---

## 🗄️ Database Schema & Data Models

CampusSentinel uses a relational PostgreSQL schema:

```mermaid
erDiagram
    LABS ||--o{ DEVICES : "contains"
    DEVICES ||--o{ DEVICE_EVENTS : "generates"
    DEVICES ||--o{ DEVICE_SNAPSHOTS : "records"

    LABS {
        int id PK
        string name UK "Unique Lab Name (e.g. Lab 101)"
        string location "Physical Room / Building"
        datetime created_at "UTC Timestamp"
    }

    DEVICES {
        int id PK
        string device_uid UK "Unique identifier (e.g. PC-101)"
        string hostname "Workstation Machine Name"
        string mac_address "Physical Hardware Address"
        string ip_address "Detected Remote IP"
        enum status "active | inactive | quarantined"
        int lab_id FK "References labs.id"
        datetime enrolled_at "Registration Timestamp"
        datetime last_seen_at "Latest Heartbeat Timestamp"
    }

    DEVICE_EVENTS {
        int id PK
        int device_id FK "References devices.id"
        enum event_type "enrolled | re_seen | status_changed"
        text detail "Event details (e.g. Device checked in)"
        datetime occurred_at "Event Timestamp"
    }

    DEVICE_SNAPSHOTS {
        int id PK
        int device_id FK "References devices.id"
        json processes "Array of running process names"
        json applications "Array of detected applications"
        datetime captured_at "Snapshot Timestamp"
    }
```

---

## 📡 REST API Reference

The backend runs on `http://127.0.0.1:8000`. Interactive OpenAPI documentation is automatically available at `http://127.0.0.1:8000/docs`.

### 1. System Health
- **`GET /health`**
  - **Description**: Verifies API operational status.
  - **Response (200 OK)**:
    ```json
    {
      "status": "ok",
      "message": "CampusSentinel API is running"
    }
    ```

### 2. Computer Labs (`/api/v1/labs`)
- **`POST /api/v1/labs`**
  - **Description**: Creates a new lab partition.
  - **Request Body**:
    ```json
    {
      "name": "Software Engineering Lab 1",
      "location": "Building C, Room 302"
    }
    ```
- **`GET /api/v1/labs`**
  - **Description**: Returns all registered labs (`skip`, `limit` query parameters supported).

### 3. Device Management (`/api/v1/devices`)
- **`POST /api/v1/devices/enroll`**
  - **Description**: Registers a new workstation or updates an existing workstation. Automatically detects connecting client IP.
  - **Request Body**:
    ```json
    {
      "device_uid": "PC-101",
      "hostname": "Lab-C-PC-101",
      "mac_address": "00:1A:2B:3C:4D:5E",
      "lab_id": 1
    }
    ```
- **`GET /api/v1/devices`**
  - **Description**: Lists registered devices. Supports optional filters: `?lab_id=1&status=active`.
- **`GET /api/v1/devices/{device_uid}`**
  - **Description**: Retrieves single device details by unique ID.

### 4. Agent Telemetry (`/api/v1/agent`)
- **`POST /api/v1/agent/heartbeat`**
  - **Description**: Ingests heartbeat signal and process snapshot from an authenticated agent.
  - **Headers**:
    - `x-device-uid`: (Required) String identifier of the device.
  - **Request Body**:
    ```json
    {
      "applications": ["chrome.exe", "code.exe"],
      "processes": ["explorer.exe", "svchost.exe", "code.exe", "python.exe"]
    }
    ```
  - **Response (200 OK)**:
    ```json
    {
      "status": "ok",
      "message": "Heartbeat accepted"
    }
    ```

### 5. Admin Operations (`/api/v1/admin`)
- **`GET /api/v1/admin/devices`**: Returns full device list with resolved `lab_name` fields.
- **`GET /api/v1/admin/devices/{device_uid}/history`**: Retrieves descending chronological audit timeline of device events.
- **`GET /api/v1/admin/devices/{device_uid}/snapshot`**: Retrieves the most recent telemetry snapshot for a device.
- **`GET /api/v1/admin/devices/{device_uid}/snapshots?limit=10`**: Retrieves historical telemetry snapshots.

---

## 📋 Prerequisites

Make sure the following tools are installed on your development machine or lab server:

- **Python**: version 3.10 or higher
- **Node.js**: version 18.x or higher (with `npm`)
- **Docker & Docker Compose**: to run the PostgreSQL container
- **Operating System**:
  - Backend & Frontend: Windows, macOS, or Linux
  - Agent: Windows, Linux (X11 for tray/dialog), or macOS

---

## 🚀 Getting Started & Installation

Follow these steps to run the complete stack locally.

### Step 1: Database Setup (Docker)

1. Clone or navigate to the repository:
   ```bash
   cd CampusSentinel
   ```

2. Prepare the environment file:
   ```bash
   # On Windows (PowerShell):
   Copy-Item backend/.env.example backend/.env

   # On Linux/macOS:
   cp backend/.env.example backend/.env
   ```

3. Start the PostgreSQL container:
   ```bash
   docker-compose up -d
   ```
   *The database will now be running on `localhost:5432` with username `postgres` and database `campus_sentinel`.*

---

### Step 2: Backend API Setup

1. Open a new terminal and navigate to `backend/`:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   # Create venv
   python -m venv .venv

   # Activate on Windows (PowerShell):
   .\.venv\Scripts\Activate.ps1
   # Activate on Windows (CMD):
   # .venv\Scripts\activate.bat
   # Activate on Linux/macOS:
   # source .venv/bin/activate
   ```

3. Install required Python packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Apply database schema migrations:
   ```bash
   alembic upgrade head
   ```

5. Launch the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

6. Verify the API is healthy:
   ```bash
   curl http://127.0.0.1:8000/health
   # Returns: {"status":"ok","message":"CampusSentinel API is running"}
   ```

---

### Step 3: Frontend Web Console Setup

1. Open a second terminal and navigate to `frontend/`:
   ```bash
   cd frontend
   ```

2. Create your local frontend environment file:
   ```bash
   # Windows (PowerShell):
   Copy-Item .env.example .env.local

   # Linux/macOS:
   cp .env.example .env.local
   ```

3. Install npm dependencies:
   ```bash
   npm install
   ```

4. Start the Vite development server:
   ```bash
   npm run dev
   ```

5. Open your browser:
   - **Device Registration**: [http://127.0.0.1:5173/](http://127.0.0.1:5173/)
   - **Admin Dashboard**: [http://127.0.0.1:5173/admin](http://127.0.0.1:5173/admin)

---

### Step 4: Endpoint Agent Setup

To simulate or run a monitored workstation endpoint:

1. Register the device via the web interface first:
   - Navigate to [http://127.0.0.1:5173/](http://127.0.0.1:5173/)
   - If no lab exists yet, create one using Swagger docs (`http://127.0.0.1:8000/docs`) or curl:
     ```bash
     curl -X POST http://127.0.0.1:8000/api/v1/labs -H "Content-Type: application/json" -d "{\"name\":\"Main Lab\",\"location\":\"Room 101\"}"
     ```
   - Complete the form with PC Number (e.g., `101`) and Device Name (e.g., `Lab-A-PC-101`). This establishes UID `PC-101`.

2. Open a third terminal and navigate to `agent/`:
   ```bash
   cd agent
   ```

3. Create and activate a dedicated virtual environment for the agent:
   ```bash
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   ```

4. Create an `agent/.env` file:
   ```env
   DEVICE_UID=PC-101
   BACKEND_URL=http://127.0.0.1:8000
   INTERVAL_SECONDS=30
   ```

5. Run the agent:
   ```bash
   python agent.py
   ```
   - An awareness notice will pop up on the screen informing the user of active monitoring.
   - A shield icon will dock in the system tray.
   - Every 30 seconds, telemetry will transmit to the backend.
   - In the Admin Dashboard (`http://127.0.0.1:5173/admin`), `PC-101` will show an active **green indicator**, and clicking its row will display live applications and process lists!

---

## 🧪 Running Automated Tests

### Backend Test Suite (Pytest)
The backend tests run against an in-memory SQLite database without requiring a live PostgreSQL instance.

```bash
cd backend
# With virtual environment activated:
pytest
```

Output includes tests covering:
- Main server health check
- Lab creation and unique constraint validation
- Device enrollment, IP tracking, and filtering
- Agent heartbeat reception and authentication
- Admin device queries and joined lab lookups
- Process snapshot capture and retrieval

### Frontend Test Suite (Vitest)
The frontend utilizes Vitest and React Testing Library to test component rendering, user interactions, and API integration mocks.

```bash
cd frontend
npm test
```

---

## ⚙️ Environment Configuration

### Backend (`backend/.env`)
| Variable | Default Value | Description |
|---|---|---|
| `PROJECT_NAME` | `CampusSentinel` | Application brand name |
| `DATABASE_URL` | `postgresql+psycopg://postgres:postgres@localhost:5432/campus_sentinel` | PostgreSQL connection string |
| `POSTGRES_USER` | `postgres` | Docker container DB username |
| `POSTGRES_PASSWORD` | `postgres` | Docker container DB password |
| `POSTGRES_DB` | `campus_sentinel` | Docker container DB database name |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000,http://localhost:5173,http://127.0.0.1:5173` | Allowed CORS origins for web clients |

### Frontend (`frontend/.env.local`)
| Variable | Default Value | Description |
|---|---|---|
| `VITE_API_BASE_URL` | `http://127.0.0.1:8000` | Target URL of the backend API |

### Agent (`agent/.env`)
| Variable | Default Value | Description |
|---|---|---|
| `DEVICE_UID` | `PC-101` | Matching unique device ID registered in the system |
| `BACKEND_URL` | `http://127.0.0.1:8000` | Target URL of the backend API |
| `INTERVAL_SECONDS` | `60` | Telemetry transmission frequency in seconds |

---

## 🗺️ Roadmap

- [x] **Phase 1: Backend Foundation & Data Architecture** (FastAPI, PostgreSQL, Alembic migrations)
- [x] **Phase 2: Device & Lab Management** (Enrollment, IP resolution, lifecycle event logging)
- [x] **Phase 3: Administrative Frontend** (Registration form, real-time table, inspection drawer)
- [x] **Phase 4: Transparent Endpoint Agent** (Notice modal, tray icon, process telemetry, heartbeats)
- [ ] **Phase 5: Authentication & RBAC**:
  - JWT authentication for administrative access (Admin, Lab Technician, Auditor roles).
  - Mutual TLS (mTLS) or pre-shared key (PSK) authentication for agent heartbeats.
- [ ] **Phase 6: Policy Enforcement & Automated Quarantine**:
  - Blacklisted process alerts (e.g., unauthorized torrent clients, crypto miners).
  - One-click device quarantine directly from the administrative dashboard.
- [ ] **Phase 7: Network Access Control (NAC) Integrations**:
  - Integration with 802.1X RADIUS / dynamic VLAN assignment to isolate unmanaged or quarantined machines.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE) — feel free to adapt and expand it for your campus or educational institution.

# bruebox_cloud — Single POS Cloud Backend

This repository provides a simple cloud backend for a single POS terminal integration. It is designed to work with the Glory POS Application at:

[Glory POS Application](https://github.com/a1364t/Glory-POS-Application)

The service supports a command queue for a single POS terminal and includes special handling for change/cancel workflows.

The project has deployed on pythonanywhere [HERE](https://talaeia.pythonanywhere.com/api/fetch/)

## Features

- Single POS integration with API-based authentication
- Command queue management for one POS terminal
- Supported commands: `OPEN`, `OCCUPY`, `RELEASE`, `CLOSE`, `STATUS`, `CHANGE`, `RESET`, `CANCEL`
- Prevents retrying `CHANGE` commands when a pending `CANCEL` request exists
- Uses SQLite for local storage
- REST API endpoints for fetching commands and submitting results

## POS Integration

This backend is intended to integrate with the Glory POS application by exchanging command requests and results.

- The POS device fetches the next available command from the cloud
- The POS device executes the command and reports the result back
- For `CHANGE` commands, a pending `CANCEL` will stop further retries and mark the command as `DEAD`

## Setup

1. Clone this repository.
2. Create and activate a Python virtual environment.

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Make sure the `.env` file is present in the project root and contains `DJANGO_SECRET_KEY`.

5. Run Django migrations:

   ```bash
   python manage.py migrate
   ```

6. Start the server:

   ```bash
   python manage.py runserver
   ```

## API Endpoints

- `GET /fetch/` — Fetch the next pending command for the authenticated POS
- `POST /result/<command_id>/` — Submit the execution result for a command

## Notes

- Authentication is handled in `pos_api/auth.py`
- POS command logic is implemented in `pos_api/views.py`
- Command definitions and state are stored in `pos_api/models.py`

## Requirements

See `requirements.txt` for the required Python packages.

# PREDIS Repository

## Overview

This repository contains the implementation of the PREDIS system, which is designed for real-time monitoring and data acquisition from devices in nuclear waste management environments. The software architecture employs object-oriented design principles, with a focus on flexibility, scalability, and maintainability.

## Key Components

- **Registry**: Manages dynamic device registration using the Singleton pattern, ensuring centralized control over device management.
- **Core**: Acts as the coordination layer, handling communication between subsystems like scheduling, file management, and device interaction.
- **DeviceInterface & ElectronicAPIs**: Provide abstraction for hardware communication, allowing flexibility in hardware interactions.
- **Scheduler**: Manages operator-defined tasks such as data downloads and device configuration.

## Project Structure

- `backend/`: Contains the core backend logic, managing both frontend and electronic APIs.
- `db/`: Database scripts and schema.
- `post_ops/`: Post-processing scripts for handling collected data.
- `predis-docker-compose.yml`: Docker configuration to run the system.
- `device_wifi_wrapper.py`: Python replica of the device's firmware.

## Prerequisites

- [Docker](https://www.docker.com/)
- [docker-compose](https://docs.docker.com/compose/)

## Usage

1. Clone the repository:

   ```bash
   git clone https://github.com/mikjkd/PREDIS_repo.git
   cd PREDIS_repo
    ```
2. Build and start the services using Docker Compose:
    ```bash
   docker-compose -f predis-docker-compose.yml up --build
   ```
3. Configure devices and let interact it with the Backend:
    ```bash
    python device_wifi_wrapper.py
   ```

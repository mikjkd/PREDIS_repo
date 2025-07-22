# PREDIS Repository

## Overview

This repository contains the implementation of the PREDIS system, which is designed for real-time monitoring and data acquisition from devices in nuclear waste management environments. The software architecture employs object-oriented design principles, with a focus on flexibility, scalability, and maintainability.

Within the scope of this project, custom detectors capable of monitoring alpha and gamma radiation emissions were developed. These detectors are controlled by read-out boards, equipped with an ESP32 microcontroller programmed to expose an HTTP web server for configuring detector parameters.

After testing the detectors and read-out electronics in the laboratory at INFN with known sources, a demonstration test was conducted at UJV Research centre - Czech Republic.

## Key Components

- **Registry**: Manages dynamic device registration using the Singleton pattern, ensuring centralized control over device management.
- **Core**: Acts as the coordination layer, handling communication between subsystems like scheduling, file management, and device interaction.
- **DeviceInterface & ElectronicAPIs**: Provide abstraction for hardware communication, allowing flexibility in hardware interactions.
- **Scheduler**: Manages operator-defined tasks such as data downloads and device configuration.
  
## Tech Stack
- Python;
- Flask;
- PostgreSQL;
- Docker;
- Mercure.

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
## License
This project is licensed under the MIT License

## Acknowledgement
This work has been financed within the framework of PREDIS (Pre-disposal management of radioactive waste, 
Euratom research and training programme, grant agreement No 945098).

If you use this repository in your work, please cite the following paper:

Di Giovanni, M., Verde, L., Campanile, L., Romoli, M., Sabbarese, C., & Marrone, S. (2025). Assessing Safety and Sustainability of a Monitoring System for Nuclear Waste Management. IEEE Access, 13, 120486–120505. https://doi.org/10.1109/ACCESS.2025.3586735

```
@ARTICLE{11077155,
  author={Di Giovanni, Michele and Verde, Laura and Campanile, Lelio and Romoli, Mauro and Sabbarese, Carlo and Marrone, Stefano}, 
  journal={IEEE Access}, 
  title={Assessing Safety and Sustainability of a Monitoring System for Nuclear Waste Management}, 
  year={2025},
  volume={13},
  number={},
  pages={120486-120505},
  keywords={Monitoring;Radioactive pollution;Safety;Sustainable development;Unified modeling language;Protection;Computer architecture;Internet of Things;Standards;Decision support systems;Decision support system;pre-disposal nuclear waste;Internet of Things;monitoring system;safety assessment;sustainability assessment},
  doi={10.1109/ACCESS.2025.3586735}
}
```

Folder Structure:

- codice: 
    - analisi_dati:
      - script utilizzati per analizzare le misure delle schede
    - backend:
      - codice backend (nodo centrale)
    - server:
      - codice server scheda elettronica
    - requirements.txt

##analisi dati:

##backend:
Codice del nodo centrale.
Lo scopo è quello di offrire due interfacce: da un lato le API per il frontend
e dall'altro le API per l'elettronica.

![monolithic backend](images/monolithic_backend.jpg)

I vari casi d'uso sono definiti dai sequence diagram:

- Data is ready: il dispositivo elettronico è pronto a scambiare dati con il nodo centrale
![](images/data_is_ready_sequence.jpg)

- Device registration: il dispositivo elettronico si collega alla rete, registrandosi e ricevendo un ip
![](images/device_registration.jpg)



##server:


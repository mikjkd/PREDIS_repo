CREATE TABLE IF NOT EXISTS CONFIG
(
    id                  SERIAL NOT NULL,
    thrA                float4,
    thrB                float4,
    HV                  float4,
    curr_datetime       timestamp,
    alarm               time,
    acquisition_time    int4,
    preacquisition_time int4,
    delay_hv            float4,
    PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS DEVICE
(
    id       varchar(50) NOT NULL,
    ip       varchar(15) NOT NULL,
    port     int         NOT NULL,
    CONFIGid int4,
    PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS DEVICE_SCHEDULE
(
    DEVICEid   varchar(50) NOT NULL,
    SCHEDULEid int4        NOT NULL,
    PRIMARY KEY (DEVICEid, SCHEDULEid)
);
CREATE TABLE IF NOT EXISTS EVENT
(
    DEVICEid       varchar(50) NOT NULL,
    id             SERIAL      NOT NULL,
    timestamp      timestamp,
    duration       int,
    will_wakeup_at time,
    PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS MEASURE
(
    id                    SERIAL      NOT NULL,
    date                  date,
    time                  time,
    temperature_s1        float4,
    temperature_s2        float4,
    set_acq_time          int4,
    eff_acq_time          int4,
    set_hv                float4,
    curr_hv               float4,
    no_data               int,
    current               float4,
    thA                   float4,
    thB                   float4,
    chA_count             float4,
    chB_count             float4,
    count_coincidences    int4,
    analyzed_coincidences int4,
    DEVICEid              varchar(50) NOT NULL,
    PRIMARY KEY (id)
);
CREATE TABLE IF NOT EXISTS SCHEDULE
(
    id              SERIAL NOT NULL,
    start_ts        timestamp,
    end_ts          timestamp,
    wake_up_every   float4,
    measure_time_ms int4,
    PRIMARY KEY (id)
);
ALTER TABLE MEASURE
    ADD CONSTRAINT FKMEASURE300818 FOREIGN KEY (DEVICEid) REFERENCES DEVICE (id);
ALTER TABLE DEVICE
    ADD CONSTRAINT FKDEVICE831109 FOREIGN KEY (CONFIGid) REFERENCES CONFIG (id);
ALTER TABLE DEVICE_SCHEDULE
    ADD CONSTRAINT FKDEVICE_SCH217831 FOREIGN KEY (DEVICEid) REFERENCES DEVICE (id);
ALTER TABLE DEVICE_SCHEDULE
    ADD CONSTRAINT FKDEVICE_SCH467924 FOREIGN KEY (SCHEDULEid) REFERENCES SCHEDULE (id);
ALTER TABLE EVENT
    ADD CONSTRAINT FKEVENT650919 FOREIGN KEY (DEVICEid) REFERENCES DEVICE (id);

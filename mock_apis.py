"""
mock_apis.py — Mock podaci u Berlin Group NextGenPSD2 formatu
Hakaton MVP | FinAssist AI
"""


def get_account() -> dict:
    """
    Berlin Group: GET /v1/accounts/{account-id}
    Vraća podatke o bankovnom računu i saldu.
    """
    return {
        "data": {
            "account": {
                "resourceId": "a1b2c3d4-0001-0001-0001-aabbccddeeff",
                "currency": "RSD",
                "cashAccountType": "Checking",
                "status": "enabled",
                "bic": "AIKBRS22",
                "iban": "RS35105008123456789"
            },
            "balances": [
                {
                    "balanceType": "closingBooked",
                    "balanceAmount": {"currency": "RSD", "amount": "1842500.00"},
                    "lastChangeDateTime": "2025-03-28T18:00:00Z"
                },
                {
                    "balanceType": "expected",
                    "balanceAmount": {"currency": "RSD", "amount": "1842500.00"},
                    "lastChangeDateTime": "2025-03-28T18:00:00Z"
                }
            ]
        },
        "links": {
            "self": {"href": "/v1/accounts/a1b2c3d4-0001-0001-0001-aabbccddeeff/balances"},
            "transactions": {"href": "/v1/accounts/a1b2c3d4-0001-0001-0001-aabbccddeeff/transactions"}
        },
        "meta": {"totalResults": 1, "timestamp": "2025-03-28T18:05:00Z"}
    }


def get_bank_transactions() -> dict:
    """
    Berlin Group: GET /v1/accounts/{account-id}/transactions
    30 knjizenih transakcija za poslednjih ~3 meseca.
    Pozitivan amount = uplata (prihod), negativan = isplata (trosak).
    """
    OUR_IBAN = "RS35105008123456789"

    booked = [
        # ── JANUAR ──
        {"transactionId": "TXN-2025-001", "bookingDate": "2025-01-03", "valueDate": "2025-01-03",
         "transactionAmount": {"currency": "RSD", "amount": "580000.00"},
         "creditorAccount": {"iban": OUR_IBAN}, "debtorName": "Telekom Srbija a.d.",
         "debtorAccount": {"iban": "RS35160005000056781234"},
         "remittanceInformationUnstructured": "Uplata po ugovoru br. TS-2024-089",
         "bankTransactionCode": "PMNT-RCDT-ESCT"},

        {"transactionId": "TXN-2025-002", "bookingDate": "2025-01-05", "valueDate": "2025-01-05",
         "transactionAmount": {"currency": "RSD", "amount": "-120000.00"},
         "creditorName": "Poslovni Centar Beograd d.o.o.",
         "creditorAccount": {"iban": "RS35265001000087654321"},
         "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Zakup poslovnog prostora januar 2025.",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        {"transactionId": "TXN-2025-003", "bookingDate": "2025-01-07", "valueDate": "2025-01-07",
         "transactionAmount": {"currency": "RSD", "amount": "-18400.00"},
         "creditorName": "EPS Distribucija d.o.o.",
         "creditorAccount": {"iban": "RS35908500000000100001"},
         "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Racun za struju 12/2024",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        {"transactionId": "TXN-2025-004", "bookingDate": "2025-01-10", "valueDate": "2025-01-10",
         "transactionAmount": {"currency": "RSD", "amount": "340000.00"},
         "creditorAccount": {"iban": OUR_IBAN}, "debtorName": "NIS a.d. Novi Sad",
         "debtorAccount": {"iban": "RS35840000000000123401"},
         "remittanceInformationUnstructured": "Uplata faktura NIS-2025-0010",
         "bankTransactionCode": "PMNT-RCDT-ESCT"},

        {"transactionId": "TXN-2025-005", "bookingDate": "2025-01-12", "valueDate": "2025-01-12",
         "transactionAmount": {"currency": "RSD", "amount": "-9750.00"},
         "creditorName": "Office Depo Srbija d.o.o.",
         "creditorAccount": {"iban": "RS35200001000009876500"},
         "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Kancelarijski materijal - racun 8821",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        {"transactionId": "TXN-2025-006", "bookingDate": "2025-01-15", "valueDate": "2025-01-15",
         "transactionAmount": {"currency": "RSD", "amount": "-310000.00"},
         "creditorName": "Interni - Isplata plata",
         "creditorAccount": {"iban": OUR_IBAN}, "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Isplata neto plata zaposleni januar 2025.",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        {"transactionId": "TXN-2025-007", "bookingDate": "2025-01-18", "valueDate": "2025-01-18",
         "transactionAmount": {"currency": "RSD", "amount": "210000.00"},
         "creditorAccount": {"iban": OUR_IBAN}, "debtorName": "Comtrade Group d.o.o.",
         "debtorAccount": {"iban": "RS35105000000000567890"},
         "remittanceInformationUnstructured": "Uplata usluge integracije Q4-2024",
         "bankTransactionCode": "PMNT-RCDT-ESCT"},

        {"transactionId": "TXN-2025-008", "bookingDate": "2025-01-22", "valueDate": "2025-01-22",
         "transactionAmount": {"currency": "RSD", "amount": "-24000.00"},
         "creditorName": "Microsoft Ireland Operations Ltd.",
         "creditorAccount": {"iban": "IE29AIBK93115212345678"},
         "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Microsoft 365 Business - godisnja pretplata",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        {"transactionId": "TXN-2025-009", "bookingDate": "2025-01-25", "valueDate": "2025-01-25",
         "transactionAmount": {"currency": "RSD", "amount": "-15200.00"},
         "creditorName": "OMV Srbija d.o.o.",
         "creditorAccount": {"iban": "RS35250004000033219900"},
         "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Gorivo vozni park januar 2025.",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        {"transactionId": "TXN-2025-010", "bookingDate": "2025-01-28", "valueDate": "2025-01-28",
         "transactionAmount": {"currency": "RSD", "amount": "160000.00"},
         "creditorAccount": {"iban": OUR_IBAN}, "debtorName": "Mercator-S d.o.o.",
         "debtorAccount": {"iban": "RS35105500000000998811"},
         "remittanceInformationUnstructured": "Uplata racun EF-2025-001",
         "bankTransactionCode": "PMNT-RCDT-ESCT"},

        # ── FEBRUAR ──
        {"transactionId": "TXN-2025-011", "bookingDate": "2025-02-03", "valueDate": "2025-02-03",
         "transactionAmount": {"currency": "RSD", "amount": "490000.00"},
         "creditorAccount": {"iban": OUR_IBAN}, "debtorName": "Delhaize Srbija d.o.o.",
         "debtorAccount": {"iban": "RS35265010000000771234"},
         "remittanceInformationUnstructured": "Uplata usluge konsaltinga feb 2025.",
         "bankTransactionCode": "PMNT-RCDT-ESCT"},

        {"transactionId": "TXN-2025-012", "bookingDate": "2025-02-05", "valueDate": "2025-02-05",
         "transactionAmount": {"currency": "RSD", "amount": "-120000.00"},
         "creditorName": "Poslovni Centar Beograd d.o.o.",
         "creditorAccount": {"iban": "RS35265001000087654321"},
         "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Zakup poslovnog prostora februar 2025.",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        {"transactionId": "TXN-2025-013", "bookingDate": "2025-02-07", "valueDate": "2025-02-07",
         "transactionAmount": {"currency": "RSD", "amount": "-6800.00"},
         "creditorName": "SBB d.o.o.",
         "creditorAccount": {"iban": "RS35300000000000456700"},
         "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Internet usluga februar 2025.",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        {"transactionId": "TXN-2025-014", "bookingDate": "2025-02-10", "valueDate": "2025-02-10",
         "transactionAmount": {"currency": "RSD", "amount": "275000.00"},
         "creditorAccount": {"iban": OUR_IBAN}, "debtorName": "Bambi a.d. Pozarevac",
         "debtorAccount": {"iban": "RS35840005000011223300"},
         "remittanceInformationUnstructured": "Uplata distribucija Q1 2025.",
         "bankTransactionCode": "PMNT-RCDT-ESCT"},

        {"transactionId": "TXN-2025-015", "bookingDate": "2025-02-12", "valueDate": "2025-02-12",
         "transactionAmount": {"currency": "RSD", "amount": "-32500.00"},
         "creditorName": "Auto centar Milosevic d.o.o.",
         "creditorAccount": {"iban": "RS35170002000000119988"},
         "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Servis i registracija vozila VW Crafter",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        {"transactionId": "TXN-2025-016", "bookingDate": "2025-02-15", "valueDate": "2025-02-15",
         "transactionAmount": {"currency": "RSD", "amount": "-310000.00"},
         "creditorName": "Interni - Isplata plata",
         "creditorAccount": {"iban": OUR_IBAN}, "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Isplata neto plata zaposleni februar 2025.",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        {"transactionId": "TXN-2025-017", "bookingDate": "2025-02-18", "valueDate": "2025-02-18",
         "transactionAmount": {"currency": "RSD", "amount": "185000.00"},
         "creditorAccount": {"iban": OUR_IBAN}, "debtorName": "Knjaz Milos a.d. Arandelovac",
         "debtorAccount": {"iban": "RS35200600000000334411"},
         "remittanceInformationUnstructured": "Uplata racun EF-2025-004",
         "bankTransactionCode": "PMNT-RCDT-ESCT"},

        {"transactionId": "TXN-2025-018", "bookingDate": "2025-02-20", "valueDate": "2025-02-20",
         "transactionAmount": {"currency": "RSD", "amount": "-45000.00"},
         "creditorName": "Digital Media Group d.o.o.",
         "creditorAccount": {"iban": "RS35105001000000228844"},
         "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Marketing kampanja Google/Meta feb 2025.",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        {"transactionId": "TXN-2025-019", "bookingDate": "2025-02-24", "valueDate": "2025-02-24",
         "transactionAmount": {"currency": "RSD", "amount": "320000.00"},
         "creditorAccount": {"iban": OUR_IBAN}, "debtorName": "Saga d.o.o. Beograd",
         "debtorAccount": {"iban": "RS35105002000000667722"},
         "remittanceInformationUnstructured": "Uplata IT usluge februar 2025.",
         "bankTransactionCode": "PMNT-RCDT-ESCT"},

        {"transactionId": "TXN-2025-020", "bookingDate": "2025-02-27", "valueDate": "2025-02-27",
         "transactionAmount": {"currency": "RSD", "amount": "-98000.00"},
         "creditorName": "Tehnomanija d.o.o.",
         "creditorAccount": {"iban": "RS35908000000000445599"},
         "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Nabavka laptop Dell i monitor - racun 44512",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        # ── MART ──
        {"transactionId": "TXN-2025-021", "bookingDate": "2025-03-03", "valueDate": "2025-03-03",
         "transactionAmount": {"currency": "RSD", "amount": "620000.00"},
         "creditorAccount": {"iban": OUR_IBAN}, "debtorName": "Air Serbia a.d.",
         "debtorAccount": {"iban": "RS35160010000000889900"},
         "remittanceInformationUnstructured": "Uplata ugovor AIR-2024-112 mart 2025.",
         "bankTransactionCode": "PMNT-RCDT-ESCT"},

        {"transactionId": "TXN-2025-022", "bookingDate": "2025-03-05", "valueDate": "2025-03-05",
         "transactionAmount": {"currency": "RSD", "amount": "-120000.00"},
         "creditorName": "Poslovni Centar Beograd d.o.o.",
         "creditorAccount": {"iban": "RS35265001000087654321"},
         "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Zakup poslovnog prostora mart 2025.",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        {"transactionId": "TXN-2025-023", "bookingDate": "2025-03-08", "valueDate": "2025-03-08",
         "transactionAmount": {"currency": "RSD", "amount": "-21300.00"},
         "creditorName": "EPS Distribucija d.o.o.",
         "creditorAccount": {"iban": "RS35908500000000100001"},
         "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Racun za struju 02/2025",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        {"transactionId": "TXN-2025-024", "bookingDate": "2025-03-10", "valueDate": "2025-03-10",
         "transactionAmount": {"currency": "RSD", "amount": "410000.00"},
         "creditorAccount": {"iban": OUR_IBAN}, "debtorName": "HBIS Group Serbia Iron and Steel",
         "debtorAccount": {"iban": "RS35105012000000334455"},
         "remittanceInformationUnstructured": "Uplata usluge logistike mart 2025.",
         "bankTransactionCode": "PMNT-RCDT-ESCT"},

        {"transactionId": "TXN-2025-025", "bookingDate": "2025-03-13", "valueDate": "2025-03-13",
         "transactionAmount": {"currency": "RSD", "amount": "-7200.00"},
         "creditorName": "Papir Servis d.o.o.",
         "creditorAccount": {"iban": "RS35200002000000778811"},
         "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Kancelarijski materijal mart - racun 1092",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        {"transactionId": "TXN-2025-026", "bookingDate": "2025-03-15", "valueDate": "2025-03-15",
         "transactionAmount": {"currency": "RSD", "amount": "-310000.00"},
         "creditorName": "Interni - Isplata plata",
         "creditorAccount": {"iban": OUR_IBAN}, "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Isplata neto plata zaposleni mart 2025.",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        {"transactionId": "TXN-2025-027", "bookingDate": "2025-03-18", "valueDate": "2025-03-18",
         "transactionAmount": {"currency": "RSD", "amount": "240000.00"},
         "creditorAccount": {"iban": OUR_IBAN}, "debtorName": "Carlsberg Srbija d.o.o.",
         "debtorAccount": {"iban": "RS35840009000000112233"},
         "remittanceInformationUnstructured": "Uplata usluge distribucije Q1 2025.",
         "bankTransactionCode": "PMNT-RCDT-ESCT"},

        {"transactionId": "TXN-2025-028", "bookingDate": "2025-03-21", "valueDate": "2025-03-21",
         "transactionAmount": {"currency": "RSD", "amount": "-55000.00"},
         "creditorName": "Advokatska kancelarija Petrovic i Jankovic",
         "creditorAccount": {"iban": "RS35105003000000556677"},
         "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Pravno savetovanje mart 2025 - ugovor PJ-089",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},

        {"transactionId": "TXN-2025-029", "bookingDate": "2025-03-25", "valueDate": "2025-03-25",
         "transactionAmount": {"currency": "RSD", "amount": "380000.00"},
         "creditorAccount": {"iban": OUR_IBAN}, "debtorName": "MK Group d.o.o.",
         "debtorAccount": {"iban": "RS35160015000000990011"},
         "remittanceInformationUnstructured": "Uplata konsalting usluge MK-2025-03",
         "bankTransactionCode": "PMNT-RCDT-ESCT"},

        {"transactionId": "TXN-2025-030", "bookingDate": "2025-03-28", "valueDate": "2025-03-28",
         "transactionAmount": {"currency": "RSD", "amount": "-18600.00"},
         "creditorName": "Adobe Systems EMEA Ltd.",
         "creditorAccount": {"iban": "IE12BOFI90001710040000"},
         "debtorAccount": {"iban": OUR_IBAN},
         "remittanceInformationUnstructured": "Adobe Creative Cloud godisnja pretplata",
         "bankTransactionCode": "PMNT-DBTDP-ESCT"},
    ]

    return {
        "data": {
            "account": {"iban": OUR_IBAN},
            "transactions": {"booked": booked, "pending": []}
        },
        "links": {
            "self": {"href": "/v1/accounts/a1b2c3d4-0001-0001-0001-aabbccddeeff/transactions"},
            "account": {"href": "/v1/accounts/a1b2c3d4-0001-0001-0001-aabbccddeeff"}
        },
        "meta": {"totalResults": len(booked), "timestamp": "2025-03-28T18:05:00Z"}
    }


def get_efakture() -> dict:
    """
    Mock eFakture u UBL 2.1 / Berlin Group-inspired formatu.
    status: 'Approved' | 'Sent' | 'Sending'
    Approved = placeno, Sent/Sending = ceka placanje.
    """
    invoices = [
        {"invoiceId": "EF-2025-001", "issueDate": "2025-01-02", "paymentDueDate": "2025-01-17",
         "status": "Approved",
         "seller": {"name": "FinAssist Solutions d.o.o.", "taxId": "101234567", "iban": "RS35105008123456789"},
         "buyer": {"name": "Telekom Srbija a.d.", "taxId": "100002590", "iban": "RS35160005000056781234"},
         "invoiceAmount": {"currency": "RSD", "taxExclusiveAmount": "483333.33", "taxAmount": "96666.67", "payableAmount": "580000.00"},
         "paymentReference": "97 56781001-2025-001"},

        {"invoiceId": "EF-2025-002", "issueDate": "2025-01-09", "paymentDueDate": "2025-01-24",
         "status": "Approved",
         "seller": {"name": "FinAssist Solutions d.o.o.", "taxId": "101234567", "iban": "RS35105008123456789"},
         "buyer": {"name": "NIS a.d. Novi Sad", "taxId": "100154163", "iban": "RS35840000000000123401"},
         "invoiceAmount": {"currency": "RSD", "taxExclusiveAmount": "283333.33", "taxAmount": "56666.67", "payableAmount": "340000.00"},
         "paymentReference": "97 56781002-2025-002"},

        {"invoiceId": "EF-2025-003", "issueDate": "2025-01-17", "paymentDueDate": "2025-02-01",
         "status": "Approved",
         "seller": {"name": "FinAssist Solutions d.o.o.", "taxId": "101234567", "iban": "RS35105008123456789"},
         "buyer": {"name": "Comtrade Group d.o.o.", "taxId": "100234567", "iban": "RS35105000000000567890"},
         "invoiceAmount": {"currency": "RSD", "taxExclusiveAmount": "175000.00", "taxAmount": "35000.00", "payableAmount": "210000.00"},
         "paymentReference": "97 56781003-2025-003"},

        {"invoiceId": "EF-2025-004", "issueDate": "2025-02-02", "paymentDueDate": "2025-02-17",
         "status": "Approved",
         "seller": {"name": "FinAssist Solutions d.o.o.", "taxId": "101234567", "iban": "RS35105008123456789"},
         "buyer": {"name": "Delhaize Srbija d.o.o.", "taxId": "100345678", "iban": "RS35265010000000771234"},
         "invoiceAmount": {"currency": "RSD", "taxExclusiveAmount": "408333.33", "taxAmount": "81666.67", "payableAmount": "490000.00"},
         "paymentReference": "97 56781004-2025-004"},

        {"invoiceId": "EF-2025-005", "issueDate": "2025-02-09", "paymentDueDate": "2025-02-24",
         "status": "Approved",
         "seller": {"name": "FinAssist Solutions d.o.o.", "taxId": "101234567", "iban": "RS35105008123456789"},
         "buyer": {"name": "Bambi a.d. Pozarevac", "taxId": "100456789", "iban": "RS35840005000011223300"},
         "invoiceAmount": {"currency": "RSD", "taxExclusiveAmount": "229166.67", "taxAmount": "45833.33", "payableAmount": "275000.00"},
         "paymentReference": "97 56781005-2025-005"},

        {"invoiceId": "EF-2025-006", "issueDate": "2025-02-17", "paymentDueDate": "2025-03-04",
         "status": "Approved",
         "seller": {"name": "FinAssist Solutions d.o.o.", "taxId": "101234567", "iban": "RS35105008123456789"},
         "buyer": {"name": "Knjaz Milos a.d. Arandelovac", "taxId": "100567890", "iban": "RS35200600000000334411"},
         "invoiceAmount": {"currency": "RSD", "taxExclusiveAmount": "154166.67", "taxAmount": "30833.33", "payableAmount": "185000.00"},
         "paymentReference": "97 56781006-2025-006"},

        {"invoiceId": "EF-2025-007", "issueDate": "2025-02-23", "paymentDueDate": "2025-03-10",
         "status": "Sent",
         "seller": {"name": "FinAssist Solutions d.o.o.", "taxId": "101234567", "iban": "RS35105008123456789"},
         "buyer": {"name": "Saga d.o.o. Beograd", "taxId": "100678901", "iban": "RS35105002000000667722"},
         "invoiceAmount": {"currency": "RSD", "taxExclusiveAmount": "266666.67", "taxAmount": "53333.33", "payableAmount": "320000.00"},
         "paymentReference": "97 56781007-2025-007"},

        {"invoiceId": "EF-2025-008", "issueDate": "2025-03-02", "paymentDueDate": "2025-03-17",
         "status": "Sent",
         "seller": {"name": "FinAssist Solutions d.o.o.", "taxId": "101234567", "iban": "RS35105008123456789"},
         "buyer": {"name": "Air Serbia a.d.", "taxId": "100789012", "iban": "RS35160010000000889900"},
         "invoiceAmount": {"currency": "RSD", "taxExclusiveAmount": "516666.67", "taxAmount": "103333.33", "payableAmount": "620000.00"},
         "paymentReference": "97 56781008-2025-008"},

        {"invoiceId": "EF-2025-009", "issueDate": "2025-03-09", "paymentDueDate": "2025-03-24",
         "status": "Sending",
         "seller": {"name": "FinAssist Solutions d.o.o.", "taxId": "101234567", "iban": "RS35105008123456789"},
         "buyer": {"name": "HBIS Group Serbia Iron and Steel", "taxId": "100890123", "iban": "RS35105012000000334455"},
         "invoiceAmount": {"currency": "RSD", "taxExclusiveAmount": "341666.67", "taxAmount": "68333.33", "payableAmount": "410000.00"},
         "paymentReference": "97 56781009-2025-009"},

        {"invoiceId": "EF-2025-010", "issueDate": "2025-03-17", "paymentDueDate": "2025-04-01",
         "status": "Sending",
         "seller": {"name": "FinAssist Solutions d.o.o.", "taxId": "101234567", "iban": "RS35105008123456789"},
         "buyer": {"name": "Carlsberg Srbija d.o.o.", "taxId": "100901234", "iban": "RS35840009000000112233"},
         "invoiceAmount": {"currency": "RSD", "taxExclusiveAmount": "200000.00", "taxAmount": "40000.00", "payableAmount": "240000.00"},
         "paymentReference": "97 56781010-2025-010"},
    ]

    return {
        "data": {"invoices": invoices},
        "links": {"self": {"href": "/v1/efakture"}},
        "meta": {"totalResults": len(invoices), "timestamp": "2025-03-28T18:05:00Z"}
    }


# ── Helper funkcije za ai_agent.py ──────────────────────────────────────────

def get_booked_transactions() -> list[dict]:
    """Samo lista knjizenih transakcija, bez Berlin Group omotaca."""
    return get_bank_transactions()["data"]["transactions"]["booked"]

def get_ukupan_prihod() -> float:
    return sum(
        float(t["transactionAmount"]["amount"])
        for t in get_booked_transactions()
        if float(t["transactionAmount"]["amount"]) > 0
    )

def get_ukupni_troskovi() -> float:
    return sum(
        float(t["transactionAmount"]["amount"])
        for t in get_booked_transactions()
        if float(t["transactionAmount"]["amount"]) < 0
    )

def get_neplacene_fakture() -> list[dict]:
    """Fakture koje nisu Approved (cekaju placanje)."""
    return [
        f for f in get_efakture()["data"]["invoices"]
        if f["status"] in ("Sent", "Sending")
    ]

def get_troskovi_po_kategoriji() -> dict:
    kategorije = {
        "Plate":       ["plata", "plate"],
        "Zakup":       ["zakup"],
        "Komunalije":  ["struju", "internet"],
        "Transport":   ["gorivo", "servis", "vozil"],
        "Softver":     ["microsoft", "adobe", "pretplata"],
        "Marketing":   ["marketing", "kampanja"],
        "Oprema":      ["laptop", "monitor", "nabavka"],
        "Usluge":      ["pravno", "advokatsk", "savetovanje"],
        "Kancelarija": ["kancelarij", "papir"],
    }
    result = {}
    for t in get_booked_transactions():
        iznos = float(t["transactionAmount"]["amount"])
        if iznos >= 0:
            continue
        opis = t["remittanceInformationUnstructured"].lower()
        kat = "Ostalo"
        for naziv, kljucne in kategorije.items():
            if any(k in opis for k in kljucne):
                kat = naziv
                break
        result[kat] = result.get(kat, 0.0) + abs(iznos)
    return result


if __name__ == "__main__":
    print("=== TEST mock_apis.py ===\n")
    txn = get_bank_transactions()
    print(f"Broj transakcija : {txn['meta']['totalResults']}")
    ef = get_efakture()
    print(f"Broj eFaktura    : {ef['meta']['totalResults']}")
    print(f"Ukupan prihod    : {get_ukupan_prihod():,.2f} RSD")
    print(f"Ukupni troskovi  : {get_ukupni_troskovi():,.2f} RSD")
    nepl = get_neplacene_fakture()
    print(f"\nFakture na cekanju ({len(nepl)}):")
    for f in nepl:
        print(f"  [{f['status']:7}] {f['invoiceId']} | {f['buyer']['name']} | {f['invoiceAmount']['payableAmount']} RSD | dospece: {f['paymentDueDate']}")
    print("\nTroskovi po kategoriji:")
    for k, v in sorted(get_troskovi_po_kategoriji().items(), key=lambda x: -x[1]):
        print(f"  {k:<15}: {v:>12,.2f} RSD")
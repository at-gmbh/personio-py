import json

json_string_employees = """
{
  "success": true,
   "metadata": {
    "total_elements": 2,
    "current_page": 0,
    "total_pages": 1
  },
  "offset": 0,
  "limit": 10,
  "data": [{
      "type": "Employee",
      "attributes": {
        "id": {
          "label": "ID",
          "value": 2116366
        },
        "first_name": {
          "label": "First name",
          "value": "Richard"
        },
        "last_name": {
          "label": "Last name",
          "value": "Stallman"
        },
        "email": {
          "label": "Email",
          "value": "rms@example.org"
        },
        "gender": {
          "label": "Gender",
          "value": "male"
        },
        "status": {
          "label": "Status",
          "value": "active"
        },
        "position": {
          "label": "Position",
          "value": "St. IGNUcius"
        },
        "supervisor": {
          "label": "Supervisor",
          "value": null
        },
        "employment_type": {
          "label": "Employment type",
          "value": "internal"
        },
        "weekly_working_hours": {
          "label": "Weekly hours",
          "value": "40"
        },
        "hire_date": {
          "label": "Hire date",
          "value": "1983-09-01T00:00:00+02:00"
        },
        "contract_end_date": {
          "label": "Contract ends",
          "value": null
        },
        "termination_date": {
          "label": "Termination date",
          "value": null
        },
        "termination_type": {
          "label": "Termination type",
          "value": ""
        },
        "termination_reason": {
          "label": "Termination reason",
          "value": ""
        },
        "probation_period_end": {
          "label": "Probation period end",
          "value": null
        },
        "created_at": {
          "label": "created_at",
          "value": "2020-07-23T19:57:57+02:00"
        },
        "last_modified_at": {
          "label": "Last modified",
          "value": "2020-07-23T19:57:57+02:00"
        },
        "subcompany": {
          "label": "Subcompany",
          "value": null
        },
        "office": {
          "label": "Office",
          "value": null
        },
        "department": {
          "label": "Department",
          "value": null
        },
        "cost_centers": {
          "label": "Cost center",
          "value": []
        },
        "holiday_calendar": {
          "label": "Public holidays",
          "value": {
            "type": "HolidayCalendar",
            "attributes": {
              "id": 1,
              "name": "Deutschland Feiertage",
              "country": "DE",
              "state": null
            }
          }
        },
        "absence_entitlement": {
          "label": "Absence entitlement",
          "value": [{
              "type": "TimeOffType",
              "attributes": {
                "id": 195824,
                "name": "Vacation",
                "entitlement": 0
              }
            }
          ]
        },
        "work_schedule": {
          "label": "Work schedule",
          "value": {
            "type": "WorkSchedule",
            "attributes": {
              "id": 232617,
              "name": "40 hours",
              "valid_from": null,
              "monday": "08:00",
              "tuesday": "08:00",
              "wednesday": "08:00",
              "thursday": "08:00",
              "friday": "08:00",
              "saturday": "00:00",
              "sunday": "00:00"
            }
          }
        },
        "fix_salary": {
          "label": "Fix salary",
          "value": 0
        },
        "fix_salary_interval": {
          "label": "Salary interval",
          "value": ""
        },
        "hourly_salary": {
          "label": "Hourly salary",
          "value": 0
        },
        "vacation_day_balance": {
          "label": "Vacation day balance",
          "value": 25
        },
        "last_working_day": {
          "label": "Last day of work",
          "value": null
        },
        "profile_picture": {
          "label": "Profile Picture",
          "value": null
        },
        "team": {
          "label": "Team",
          "value": null
        },
        "dynamic_1146702": {
          "label": "Country of Birth",
          "value": "USA"
        },
        "dynamic_1146666": {
          "label": "Birthday",
          "value": "1953-03-16T00:00:00+01:00"
        }
      }
    }, {
      "type": "Employee",
      "attributes": {
        "id": {
          "label": "ID",
          "value": 2116365
        },
        "first_name": {
          "label": "First name",
          "value": "Alan"
        },
        "last_name": {
          "label": "Last name",
          "value": "Turing"
        },
        "email": {
          "label": "Email",
          "value": "alan@example.org"
        },
        "gender": {
          "label": "Gender",
          "value": "male"
        },
        "status": {
          "label": "Status",
          "value": "active"
        },
        "position": {
          "label": "Position",
          "value": "Chief Cryptanalyst"
        },
        "supervisor": {
          "label": "Supervisor",
          "value": null
        },
        "employment_type": {
          "label": "Employment type",
          "value": "internal"
        },
        "weekly_working_hours": {
          "label": "Weekly hours",
          "value": "40"
        },
        "hire_date": {
          "label": "Hire date",
          "value": "1932-01-01T00:00:00+01:00"
        },
        "contract_end_date": {
          "label": "Contract ends",
          "value": "1954-06-07T00:00:00+01:00"
        },
        "termination_date": {
          "label": "Termination date",
          "value": null
        },
        "termination_type": {
          "label": "Termination type",
          "value": ""
        },
        "termination_reason": {
          "label": "Termination reason",
          "value": ""
        },
        "probation_period_end": {
          "label": "Probation period end",
          "value": null
        },
        "created_at": {
          "label": "created_at",
          "value": "2020-07-23T19:51:46+02:00"
        },
        "last_modified_at": {
          "label": "Last modified",
          "value": "2020-07-23T19:53:48+02:00"
        },
        "subcompany": {
          "label": "Subcompany",
          "value": null
        },
        "office": {
          "label": "Office",
          "value": null
        },
        "department": {
          "label": "Department",
          "value": null
        },
        "cost_centers": {
          "label": "Cost center",
          "value": []
        },
        "holiday_calendar": {
          "label": "Public holidays",
          "value": {
            "type": "HolidayCalendar",
            "attributes": {
              "id": 1,
              "name": "Deutschland Feiertage",
              "country": "DE",
              "state": null
            }
          }
        },
        "absence_entitlement": {
          "label": "Absence entitlement",
          "value": [{
              "type": "TimeOffType",
              "attributes": {
                "id": 195824,
                "name": "Vacation",
                "entitlement": 0
              }
            }
          ]
        },
        "work_schedule": {
          "label": "Work schedule",
          "value": {
            "type": "WorkSchedule",
            "attributes": {
              "id": 232617,
              "name": "40 hours",
              "valid_from": null,
              "monday": "08:00",
              "tuesday": "08:00",
              "wednesday": "08:00",
              "thursday": "08:00",
              "friday": "08:00",
              "saturday": "00:00",
              "sunday": "00:00"
            }
          }
        },
        "fix_salary": {
          "label": "Fix salary",
          "value": 0
        },
        "fix_salary_interval": {
          "label": "Salary interval",
          "value": ""
        },
        "hourly_salary": {
          "label": "Hourly salary",
          "value": 0
        },
        "vacation_day_balance": {
          "label": "Vacation day balance",
          "value": 25
        },
        "last_working_day": {
          "label": "Last day of work",
          "value": null
        },
        "profile_picture": {
          "label": "Profile Picture",
          "value": null
        },
        "team": {
          "label": "Team",
          "value": null
        },
        "dynamic_1146702": {
          "label": "Country of Birth",
          "value": "England"
        },
        "dynamic_1146666": {
          "label": "Birthday",
          "value": "1912-06-23T00:00:00+01:00"
        }
      }
    }, {
      "type": "Employee",
      "attributes": {
        "id": {
          "label": "ID",
          "value": 2040614
        },
        "first_name": {
          "label": "First name",
          "value": "Ada"
        },
        "last_name": {
          "label": "Last name",
          "value": "Lovelace"
        },
        "email": {
          "label": "Email",
          "value": "ada@example.org"
        },
        "gender": {
          "label": "Gender",
          "value": "female"
        },
        "status": {
          "label": "Status",
          "value": "active"
        },
        "position": {
          "label": "Position",
          "value": "first programmer ever"
        },
        "supervisor": {
          "label": "Supervisor",
          "value": null
        },
        "employment_type": {
          "label": "Employment type",
          "value": "internal"
        },
        "weekly_working_hours": {
          "label": "Weekly hours",
          "value": "35"
        },
        "hire_date": {
          "label": "Hire date",
          "value": "1835-02-01T00:00:00+00:53"
        },
        "contract_end_date": {
          "label": "Contract ends",
          "value": null
        },
        "termination_date": {
          "label": "Termination date",
          "value": null
        },
        "termination_type": {
          "label": "Termination type",
          "value": ""
        },
        "termination_reason": {
          "label": "Termination reason",
          "value": ""
        },
        "probation_period_end": {
          "label": "Probation period end",
          "value": null
        },
        "created_at": {
          "label": "created_at",
          "value": "2020-06-18T18:43:44+02:00"
        },
        "last_modified_at": {
          "label": "Last modified",
          "value": "2020-07-23T18:00:26+02:00"
        },
        "subcompany": {
          "label": "Subcompany",
          "value": null
        },
        "office": {
          "label": "Office",
          "value": null
        },
        "department": {
          "label": "Department",
          "value": {
            "type": "Department",
            "attributes": {
              "id": 625448,
              "name": "Operations"
            }
          }
        },
        "cost_centers": {
          "label": "Cost center",
          "value": []
        },
        "holiday_calendar": {
          "label": "Public holidays",
          "value": {
            "type": "HolidayCalendar",
            "attributes": {
              "id": 1,
              "name": "Deutschland Feiertage",
              "country": "DE",
              "state": null
            }
          }
        },
        "absence_entitlement": {
          "label": "Absence entitlement",
          "value": [{
              "type": "TimeOffType",
              "attributes": {
                "id": 195824,
                "name": "Vacation",
                "entitlement": 0
              }
            }
          ]
        },
        "work_schedule": {
          "label": "Work schedule",
          "value": {
            "type": "WorkSchedule",
            "attributes": {
              "id": 232617,
              "name": "Vollzeit, 40 Stunden ohne Zeiterfassung, (Mo,Di,Mi,Do,Fr) ",
              "valid_from": null,
              "monday": "08:00",
              "tuesday": "08:00",
              "wednesday": "08:00",
              "thursday": "08:00",
              "friday": "08:00",
              "saturday": "00:00",
              "sunday": "00:00"
            }
          }
        },
        "fix_salary": {
          "label": "Fix salary",
          "value": 0
        },
        "fix_salary_interval": {
          "label": "Salary interval",
          "value": ""
        },
        "hourly_salary": {
          "label": "Hourly salary",
          "value": 0
        },
        "vacation_day_balance": {
          "label": "Vacation day balance",
          "value": 25
        },
        "last_working_day": {
          "label": "Last day of work",
          "value": null
        },
        "profile_picture": {
          "label": "Profile Picture",
          "value": null
        },
        "team": {
          "label": "Team",
          "value": null
        },
        "dynamic_1146702": {
          "label": "Country of Birth",
          "value": "England"
        },
        "dynamic_1146666": {
          "label": "Birthday",
          "value": "1815-12-10T00:00:00+01:00"
        }
      }
    }
  ]
}
"""
json_dict_employees = json.loads(json_string_employees)

json_string_employees_page1 = """{
  "success": true,
   "metadata": {
    "total_elements": 150,
    "current_page": 0,
    "total_pages": 2
  },
  "offset": 0,
  "limit": 100,
  "data": [{
      "type": "Employee",
      "attributes": {
        "id": {
          "label": "ID",
          "value": 2116366
        },
        "first_name": {
          "label": "First name",
          "value": "Richard"
        },
        "last_name": {
          "label": "Last name",
          "value": "Stallman"
        },
        "email": {
          "label": "Email",
          "value": "rms@example.org"
        },
        "gender": {
          "label": "Gender",
          "value": "male"
        },
        "status": {
          "label": "Status",
          "value": "active"
        },
        "position": {
          "label": "Position",
          "value": "St. IGNUcius"
        },
        "supervisor": {
          "label": "Supervisor",
          "value": null
        },
        "employment_type": {
          "label": "Employment type",
          "value": "internal"
        },
        "weekly_working_hours": {
          "label": "Weekly hours",
          "value": "40"
        },
        "hire_date": {
          "label": "Hire date",
          "value": "1983-09-01T00:00:00+02:00"
        },
        "contract_end_date": {
          "label": "Contract ends",
          "value": null
        },
        "termination_date": {
          "label": "Termination date",
          "value": null
        },
        "termination_type": {
          "label": "Termination type",
          "value": ""
        },
        "termination_reason": {
          "label": "Termination reason",
          "value": ""
        },
        "probation_period_end": {
          "label": "Probation period end",
          "value": null
        },
        "created_at": {
          "label": "created_at",
          "value": "2020-07-23T19:57:57+02:00"
        },
        "last_modified_at": {
          "label": "Last modified",
          "value": "2020-07-23T19:57:57+02:00"
        },
        "subcompany": {
          "label": "Subcompany",
          "value": null
        },
        "office": {
          "label": "Office",
          "value": null
        },
        "department": {
          "label": "Department",
          "value": null
        },
        "cost_centers": {
          "label": "Cost center",
          "value": []
        },
        "holiday_calendar": {
          "label": "Public holidays",
          "value": {
            "type": "HolidayCalendar",
            "attributes": {
              "id": 1,
              "name": "Deutschland Feiertage",
              "country": "DE",
              "state": null
            }
          }
        },
        "absence_entitlement": {
          "label": "Absence entitlement",
          "value": [{
              "type": "TimeOffType",
              "attributes": {
                "id": 195824,
                "name": "Vacation",
                "entitlement": 0
              }
            }
          ]
        },
        "work_schedule": {
          "label": "Work schedule",
          "value": {
            "type": "WorkSchedule",
            "attributes": {
              "id": 232617,
              "name": "40 hours",
              "valid_from": null,
              "monday": "08:00",
              "tuesday": "08:00",
              "wednesday": "08:00",
              "thursday": "08:00",
              "friday": "08:00",
              "saturday": "00:00",
              "sunday": "00:00"
            }
          }
        },
        "fix_salary": {
          "label": "Fix salary",
          "value": 0
        },
        "fix_salary_interval": {
          "label": "Salary interval",
          "value": ""
        },
        "hourly_salary": {
          "label": "Hourly salary",
          "value": 0
        },
        "vacation_day_balance": {
          "label": "Vacation day balance",
          "value": 25
        },
        "last_working_day": {
          "label": "Last day of work",
          "value": null
        },
        "profile_picture": {
          "label": "Profile Picture",
          "value": null
        },
        "team": {
          "label": "Team",
          "value": null
        },
        "dynamic_1146702": {
          "label": "Country of Birth",
          "value": "USA"
        },
        "dynamic_1146666": {
          "label": "Birthday",
          "value": "1953-03-16T00:00:00+01:00"
        }
      }
    }, {
      "type": "Employee",
      "attributes": {
        "id": {
          "label": "ID",
          "value": 2116365
        },
        "first_name": {
          "label": "First name",
          "value": "Alan"
        },
        "last_name": {
          "label": "Last name",
          "value": "Turing"
        },
        "email": {
          "label": "Email",
          "value": "alan@example.org"
        },
        "gender": {
          "label": "Gender",
          "value": "male"
        },
        "status": {
          "label": "Status",
          "value": "active"
        },
        "position": {
          "label": "Position",
          "value": "Chief Cryptanalyst"
        },
        "supervisor": {
          "label": "Supervisor",
          "value": null
        },
        "employment_type": {
          "label": "Employment type",
          "value": "internal"
        },
        "weekly_working_hours": {
          "label": "Weekly hours",
          "value": "40"
        },
        "hire_date": {
          "label": "Hire date",
          "value": "1932-01-01T00:00:00+01:00"
        },
        "contract_end_date": {
          "label": "Contract ends",
          "value": "1954-06-07T00:00:00+01:00"
        },
        "termination_date": {
          "label": "Termination date",
          "value": null
        },
        "termination_type": {
          "label": "Termination type",
          "value": ""
        },
        "termination_reason": {
          "label": "Termination reason",
          "value": ""
        },
        "probation_period_end": {
          "label": "Probation period end",
          "value": null
        },
        "created_at": {
          "label": "created_at",
          "value": "2020-07-23T19:51:46+02:00"
        },
        "last_modified_at": {
          "label": "Last modified",
          "value": "2020-07-23T19:53:48+02:00"
        },
        "subcompany": {
          "label": "Subcompany",
          "value": null
        },
        "office": {
          "label": "Office",
          "value": null
        },
        "department": {
          "label": "Department",
          "value": null
        },
        "cost_centers": {
          "label": "Cost center",
          "value": []
        },
        "holiday_calendar": {
          "label": "Public holidays",
          "value": {
            "type": "HolidayCalendar",
            "attributes": {
              "id": 1,
              "name": "Deutschland Feiertage",
              "country": "DE",
              "state": null
            }
          }
        },
        "absence_entitlement": {
          "label": "Absence entitlement",
          "value": [{
              "type": "TimeOffType",
              "attributes": {
                "id": 195824,
                "name": "Vacation",
                "entitlement": 0
              }
            }
          ]
        },
        "work_schedule": {
          "label": "Work schedule",
          "value": {
            "type": "WorkSchedule",
            "attributes": {
              "id": 232617,
              "name": "40 hours",
              "valid_from": null,
              "monday": "08:00",
              "tuesday": "08:00",
              "wednesday": "08:00",
              "thursday": "08:00",
              "friday": "08:00",
              "saturday": "00:00",
              "sunday": "00:00"
            }
          }
        },
        "fix_salary": {
          "label": "Fix salary",
          "value": 0
        },
        "fix_salary_interval": {
          "label": "Salary interval",
          "value": ""
        },
        "hourly_salary": {
          "label": "Hourly salary",
          "value": 0
        },
        "vacation_day_balance": {
          "label": "Vacation day balance",
          "value": 25
        },
        "last_working_day": {
          "label": "Last day of work",
          "value": null
        },
        "profile_picture": {
          "label": "Profile Picture",
          "value": null
        },
        "team": {
          "label": "Team",
          "value": null
        },
        "dynamic_1146702": {
          "label": "Country of Birth",
          "value": "England"
        },
        "dynamic_1146666": {
          "label": "Birthday",
          "value": "1912-06-23T00:00:00+01:00"
        }
      }
    }, {
      "type": "Employee",
      "attributes": {
        "id": {
          "label": "ID",
          "value": 2040614
        },
        "first_name": {
          "label": "First name",
          "value": "Ada"
        },
        "last_name": {
          "label": "Last name",
          "value": "Lovelace"
        },
        "email": {
          "label": "Email",
          "value": "ada@example.org"
        },
        "gender": {
          "label": "Gender",
          "value": "female"
        },
        "status": {
          "label": "Status",
          "value": "active"
        },
        "position": {
          "label": "Position",
          "value": "first programmer ever"
        },
        "supervisor": {
          "label": "Supervisor",
          "value": null
        },
        "employment_type": {
          "label": "Employment type",
          "value": "internal"
        },
        "weekly_working_hours": {
          "label": "Weekly hours",
          "value": "35"
        },
        "hire_date": {
          "label": "Hire date",
          "value": "1835-02-01T00:00:00+00:53"
        },
        "contract_end_date": {
          "label": "Contract ends",
          "value": null
        },
        "termination_date": {
          "label": "Termination date",
          "value": null
        },
        "termination_type": {
          "label": "Termination type",
          "value": ""
        },
        "termination_reason": {
          "label": "Termination reason",
          "value": ""
        },
        "probation_period_end": {
          "label": "Probation period end",
          "value": null
        },
        "created_at": {
          "label": "created_at",
          "value": "2020-06-18T18:43:44+02:00"
        },
        "last_modified_at": {
          "label": "Last modified",
          "value": "2020-07-23T18:00:26+02:00"
        },
        "subcompany": {
          "label": "Subcompany",
          "value": null
        },
        "office": {
          "label": "Office",
          "value": null
        },
        "department": {
          "label": "Department",
          "value": {
            "type": "Department",
            "attributes": {
              "id": 625448,
              "name": "Operations"
            }
          }
        },
        "cost_centers": {
          "label": "Cost center",
          "value": []
        },
        "holiday_calendar": {
          "label": "Public holidays",
          "value": {
            "type": "HolidayCalendar",
            "attributes": {
              "id": 1,
              "name": "Deutschland Feiertage",
              "country": "DE",
              "state": null
            }
          }
        },
        "absence_entitlement": {
          "label": "Absence entitlement",
          "value": [{
              "type": "TimeOffType",
              "attributes": {
                "id": 195824,
                "name": "Vacation",
                "entitlement": 0
              }
            }
          ]
        },
        "work_schedule": {
          "label": "Work schedule",
          "value": {
            "type": "WorkSchedule",
            "attributes": {
              "id": 232617,
              "name": "Vollzeit, 40 Stunden ohne Zeiterfassung, (Mo,Di,Mi,Do,Fr) ",
              "valid_from": null,
              "monday": "08:00",
              "tuesday": "08:00",
              "wednesday": "08:00",
              "thursday": "08:00",
              "friday": "08:00",
              "saturday": "00:00",
              "sunday": "00:00"
            }
          }
        },
        "fix_salary": {
          "label": "Fix salary",
          "value": 0
        },
        "fix_salary_interval": {
          "label": "Salary interval",
          "value": ""
        },
        "hourly_salary": {
          "label": "Hourly salary",
          "value": 0
        },
        "vacation_day_balance": {
          "label": "Vacation day balance",
          "value": 25
        },
        "last_working_day": {
          "label": "Last day of work",
          "value": null
        },
        "profile_picture": {
          "label": "Profile Picture",
          "value": null
        },
        "team": {
          "label": "Team",
          "value": null
        },
        "dynamic_1146702": {
          "label": "Country of Birth",
          "value": "England"
        },
        "dynamic_1146666": {
          "label": "Birthday",
          "value": "1815-12-10T00:00:00+01:00"
        }
      }
    }
  ]
}
"""
json_dict_employees_page1 = json.loads(json_string_employees_page1)

json_string_employees_page2 = """{
  "success": true,
   "metadata": {
    "total_elements": 150,
    "current_page": 1,
    "total_pages": 2
  },
  "offset": 0,
  "limit": 100,
  "data": [{
      "type": "Employee",
      "attributes": {
        "id": {
          "label": "ID",
          "value": 2116366
        },
        "first_name": {
          "label": "First name",
          "value": "Richard"
        },
        "last_name": {
          "label": "Last name",
          "value": "Stallman"
        },
        "email": {
          "label": "Email",
          "value": "rms@example.org"
        },
        "gender": {
          "label": "Gender",
          "value": "male"
        },
        "status": {
          "label": "Status",
          "value": "active"
        },
        "position": {
          "label": "Position",
          "value": "St. IGNUcius"
        },
        "supervisor": {
          "label": "Supervisor",
          "value": null
        },
        "employment_type": {
          "label": "Employment type",
          "value": "internal"
        },
        "weekly_working_hours": {
          "label": "Weekly hours",
          "value": "40"
        },
        "hire_date": {
          "label": "Hire date",
          "value": "1983-09-01T00:00:00+02:00"
        },
        "contract_end_date": {
          "label": "Contract ends",
          "value": null
        },
        "termination_date": {
          "label": "Termination date",
          "value": null
        },
        "termination_type": {
          "label": "Termination type",
          "value": ""
        },
        "termination_reason": {
          "label": "Termination reason",
          "value": ""
        },
        "probation_period_end": {
          "label": "Probation period end",
          "value": null
        },
        "created_at": {
          "label": "created_at",
          "value": "2020-07-23T19:57:57+02:00"
        },
        "last_modified_at": {
          "label": "Last modified",
          "value": "2020-07-23T19:57:57+02:00"
        },
        "subcompany": {
          "label": "Subcompany",
          "value": null
        },
        "office": {
          "label": "Office",
          "value": null
        },
        "department": {
          "label": "Department",
          "value": null
        },
        "cost_centers": {
          "label": "Cost center",
          "value": []
        },
        "holiday_calendar": {
          "label": "Public holidays",
          "value": {
            "type": "HolidayCalendar",
            "attributes": {
              "id": 1,
              "name": "Deutschland Feiertage",
              "country": "DE",
              "state": null
            }
          }
        },
        "absence_entitlement": {
          "label": "Absence entitlement",
          "value": [{
              "type": "TimeOffType",
              "attributes": {
                "id": 195824,
                "name": "Vacation",
                "entitlement": 0
              }
            }
          ]
        },
        "work_schedule": {
          "label": "Work schedule",
          "value": {
            "type": "WorkSchedule",
            "attributes": {
              "id": 232617,
              "name": "40 hours",
              "valid_from": null,
              "monday": "08:00",
              "tuesday": "08:00",
              "wednesday": "08:00",
              "thursday": "08:00",
              "friday": "08:00",
              "saturday": "00:00",
              "sunday": "00:00"
            }
          }
        },
        "fix_salary": {
          "label": "Fix salary",
          "value": 0
        },
        "fix_salary_interval": {
          "label": "Salary interval",
          "value": ""
        },
        "hourly_salary": {
          "label": "Hourly salary",
          "value": 0
        },
        "vacation_day_balance": {
          "label": "Vacation day balance",
          "value": 25
        },
        "last_working_day": {
          "label": "Last day of work",
          "value": null
        },
        "profile_picture": {
          "label": "Profile Picture",
          "value": null
        },
        "team": {
          "label": "Team",
          "value": null
        },
        "dynamic_1146702": {
          "label": "Country of Birth",
          "value": "USA"
        },
        "dynamic_1146666": {
          "label": "Birthday",
          "value": "1953-03-16T00:00:00+01:00"
        }
      }
    }, {
      "type": "Employee",
      "attributes": {
        "id": {
          "label": "ID",
          "value": 2116365
        },
        "first_name": {
          "label": "First name",
          "value": "Alan"
        },
        "last_name": {
          "label": "Last name",
          "value": "Turing"
        },
        "email": {
          "label": "Email",
          "value": "alan@example.org"
        },
        "gender": {
          "label": "Gender",
          "value": "male"
        },
        "status": {
          "label": "Status",
          "value": "active"
        },
        "position": {
          "label": "Position",
          "value": "Chief Cryptanalyst"
        },
        "supervisor": {
          "label": "Supervisor",
          "value": null
        },
        "employment_type": {
          "label": "Employment type",
          "value": "internal"
        },
        "weekly_working_hours": {
          "label": "Weekly hours",
          "value": "40"
        },
        "hire_date": {
          "label": "Hire date",
          "value": "1932-01-01T00:00:00+01:00"
        },
        "contract_end_date": {
          "label": "Contract ends",
          "value": "1954-06-07T00:00:00+01:00"
        },
        "termination_date": {
          "label": "Termination date",
          "value": null
        },
        "termination_type": {
          "label": "Termination type",
          "value": ""
        },
        "termination_reason": {
          "label": "Termination reason",
          "value": ""
        },
        "probation_period_end": {
          "label": "Probation period end",
          "value": null
        },
        "created_at": {
          "label": "created_at",
          "value": "2020-07-23T19:51:46+02:00"
        },
        "last_modified_at": {
          "label": "Last modified",
          "value": "2020-07-23T19:53:48+02:00"
        },
        "subcompany": {
          "label": "Subcompany",
          "value": null
        },
        "office": {
          "label": "Office",
          "value": null
        },
        "department": {
          "label": "Department",
          "value": null
        },
        "cost_centers": {
          "label": "Cost center",
          "value": []
        },
        "holiday_calendar": {
          "label": "Public holidays",
          "value": {
            "type": "HolidayCalendar",
            "attributes": {
              "id": 1,
              "name": "Deutschland Feiertage",
              "country": "DE",
              "state": null
            }
          }
        },
        "absence_entitlement": {
          "label": "Absence entitlement",
          "value": [{
              "type": "TimeOffType",
              "attributes": {
                "id": 195824,
                "name": "Vacation",
                "entitlement": 0
              }
            }
          ]
        },
        "work_schedule": {
          "label": "Work schedule",
          "value": {
            "type": "WorkSchedule",
            "attributes": {
              "id": 232617,
              "name": "40 hours",
              "valid_from": null,
              "monday": "08:00",
              "tuesday": "08:00",
              "wednesday": "08:00",
              "thursday": "08:00",
              "friday": "08:00",
              "saturday": "00:00",
              "sunday": "00:00"
            }
          }
        },
        "fix_salary": {
          "label": "Fix salary",
          "value": 0
        },
        "fix_salary_interval": {
          "label": "Salary interval",
          "value": ""
        },
        "hourly_salary": {
          "label": "Hourly salary",
          "value": 0
        },
        "vacation_day_balance": {
          "label": "Vacation day balance",
          "value": 25
        },
        "last_working_day": {
          "label": "Last day of work",
          "value": null
        },
        "profile_picture": {
          "label": "Profile Picture",
          "value": null
        },
        "team": {
          "label": "Team",
          "value": null
        },
        "dynamic_1146702": {
          "label": "Country of Birth",
          "value": "England"
        },
        "dynamic_1146666": {
          "label": "Birthday",
          "value": "1912-06-23T00:00:00+01:00"
        }
      }
    }, {
      "type": "Employee",
      "attributes": {
        "id": {
          "label": "ID",
          "value": 2040614
        },
        "first_name": {
          "label": "First name",
          "value": "Ada"
        },
        "last_name": {
          "label": "Last name",
          "value": "Lovelace"
        },
        "email": {
          "label": "Email",
          "value": "ada@example.org"
        },
        "gender": {
          "label": "Gender",
          "value": "female"
        },
        "status": {
          "label": "Status",
          "value": "active"
        },
        "position": {
          "label": "Position",
          "value": "first programmer ever"
        },
        "supervisor": {
          "label": "Supervisor",
          "value": null
        },
        "employment_type": {
          "label": "Employment type",
          "value": "internal"
        },
        "weekly_working_hours": {
          "label": "Weekly hours",
          "value": "35"
        },
        "hire_date": {
          "label": "Hire date",
          "value": "1835-02-01T00:00:00+00:53"
        },
        "contract_end_date": {
          "label": "Contract ends",
          "value": null
        },
        "termination_date": {
          "label": "Termination date",
          "value": null
        },
        "termination_type": {
          "label": "Termination type",
          "value": ""
        },
        "termination_reason": {
          "label": "Termination reason",
          "value": ""
        },
        "probation_period_end": {
          "label": "Probation period end",
          "value": null
        },
        "created_at": {
          "label": "created_at",
          "value": "2020-06-18T18:43:44+02:00"
        },
        "last_modified_at": {
          "label": "Last modified",
          "value": "2020-07-23T18:00:26+02:00"
        },
        "subcompany": {
          "label": "Subcompany",
          "value": null
        },
        "office": {
          "label": "Office",
          "value": null
        },
        "department": {
          "label": "Department",
          "value": {
            "type": "Department",
            "attributes": {
              "id": 625448,
              "name": "Operations"
            }
          }
        },
        "cost_centers": {
          "label": "Cost center",
          "value": []
        },
        "holiday_calendar": {
          "label": "Public holidays",
          "value": {
            "type": "HolidayCalendar",
            "attributes": {
              "id": 1,
              "name": "Deutschland Feiertage",
              "country": "DE",
              "state": null
            }
          }
        },
        "absence_entitlement": {
          "label": "Absence entitlement",
          "value": [{
              "type": "TimeOffType",
              "attributes": {
                "id": 195824,
                "name": "Vacation",
                "entitlement": 0
              }
            }
          ]
        },
        "work_schedule": {
          "label": "Work schedule",
          "value": {
            "type": "WorkSchedule",
            "attributes": {
              "id": 232617,
              "name": "Vollzeit, 40 Stunden ohne Zeiterfassung, (Mo,Di,Mi,Do,Fr) ",
              "valid_from": null,
              "monday": "08:00",
              "tuesday": "08:00",
              "wednesday": "08:00",
              "thursday": "08:00",
              "friday": "08:00",
              "saturday": "00:00",
              "sunday": "00:00"
            }
          }
        },
        "fix_salary": {
          "label": "Fix salary",
          "value": 0
        },
        "fix_salary_interval": {
          "label": "Salary interval",
          "value": ""
        },
        "hourly_salary": {
          "label": "Hourly salary",
          "value": 0
        },
        "vacation_day_balance": {
          "label": "Vacation day balance",
          "value": 25
        },
        "last_working_day": {
          "label": "Last day of work",
          "value": null
        },
        "profile_picture": {
          "label": "Profile Picture",
          "value": null
        },
        "team": {
          "label": "Team",
          "value": null
        },
        "dynamic_1146702": {
          "label": "Country of Birth",
          "value": "England"
        },
        "dynamic_1146666": {
          "label": "Birthday",
          "value": "1815-12-10T00:00:00+01:00"
        }
      }
    }
  ]
}
"""
json_dict_employees_page2 = json.loads(json_string_employees_page2)

json_string_employee_ada = """
{
  "success": true,
  "data": {
    "type": "Employee",
    "attributes": {
      "id": {
        "label": "ID",
        "value": 2040614
      },
      "first_name": {
        "label": "First name",
        "value": "Ada"
      },
      "last_name": {
        "label": "Last name",
        "value": "Lovelace"
      },
      "email": {
        "label": "Email",
        "value": "ada@example.org"
      },
      "gender": {
        "label": "Gender",
        "value": "female"
      },
      "status": {
        "label": "Status",
        "value": "active"
      },
      "position": {
        "label": "Position",
        "value": "first programmer ever"
      },
      "supervisor": {
        "label": "Supervisor",
        "value": null
      },
      "employment_type": {
        "label": "Employment type",
        "value": "internal"
      },
      "weekly_working_hours": {
        "label": "Weekly hours",
        "value": "35"
      },
      "hire_date": {
        "label": "Hire date",
        "value": "1835-02-01T00:00:00+00:53"
      },
      "contract_end_date": {
        "label": "Contract ends",
        "value": null
      },
      "termination_date": {
        "label": "Termination date",
        "value": null
      },
      "termination_type": {
        "label": "Termination type",
        "value": ""
      },
      "termination_reason": {
        "label": "Termination reason",
        "value": ""
      },
      "probation_period_end": {
        "label": "Probation period end",
        "value": null
      },
      "created_at": {
        "label": "created_at",
        "value": "2020-06-18T18:43:44+02:00"
      },
      "last_modified_at": {
        "label": "Last modified",
        "value": "2020-07-23T18:00:26+02:00"
      },
      "subcompany": {
        "label": "Subcompany",
        "value": null
      },
      "office": {
        "label": "Office",
        "value": null
      },
      "department": {
        "label": "Department",
        "value": {
          "type": "Department",
          "attributes": {
            "id": 625448,
            "name": "Operations"
          }
        }
      },
      "cost_centers": {
        "label": "Cost center",
        "value": []
      },
      "holiday_calendar": {
        "label": "Public holidays",
        "value": {
          "type": "HolidayCalendar",
          "attributes": {
            "id": 1,
            "name": "Deutschland Feiertage",
            "country": "DE",
            "state": null
          }
        }
      },
      "absence_entitlement": {
        "label": "Absence entitlement",
        "value": [{
            "type": "TimeOffType",
            "attributes": {
              "id": 195824,
              "name": "Vacation",
              "entitlement": 0
            }
          }
        ]
      },
      "work_schedule": {
        "label": "Work schedule",
        "value": {
          "type": "WorkSchedule",
          "attributes": {
            "id": 232617,
            "name": "Vollzeit, 40 Stunden ohne Zeiterfassung, (Mo,Di,Mi,Do,Fr) ",
            "valid_from": null,
            "monday": "08:00",
            "tuesday": "08:00",
            "wednesday": "08:00",
            "thursday": "08:00",
            "friday": "08:00",
            "saturday": "00:00",
            "sunday": "00:00"
          }
        }
      },
      "fix_salary": {
        "label": "Fix salary",
        "value": 0
      },
      "fix_salary_interval": {
        "label": "Salary interval",
        "value": ""
      },
      "hourly_salary": {
        "label": "Hourly salary",
        "value": 0
      },
      "vacation_day_balance": {
        "label": "Vacation day balance",
        "value": 25
      },
      "last_working_day": {
        "label": "Last day of work",
        "value": null
      },
      "profile_picture": {
        "label": "Profile Picture",
        "value": null
      },
      "team": {
        "label": "Team",
        "value": null
      },
      "dynamic_1146702": {
        "label": "Country of Birth",
        "value": "England"
      },
      "dynamic_1146666": {
        "label": "Birthday",
        "value": "1815-12-10T00:00:00+01:00"
      }
    }
  }
}
"""
json_dict_employee_ada = json.loads(json_string_employee_ada)

json_string_empty_response = """
{
  "success": true,
  "data": []
}
"""
json_dict_empty_response = json.loads(json_string_empty_response)

json_string_attendance_rms = """
{
  "success": true,
  "metadata":{
        "total_elements": 3,
        "current_page":0,
        "total_pages":1
    },
  "data": [{
      "id": 33479712,
      "type": "AttendancePeriod",
      "attributes": {
        "employee": 2116366,
        "date": "1985-03-20",
        "start_time": "11:00",
        "end_time": "12:30",
        "break": 60,
        "comment": "release day! GNU Emacs Version 13 is available as free software now *yay*",
        "is_holiday": false,
        "is_on_time_off": false
      }
    }, {
      "id": 33479612,
      "type": "AttendancePeriod",
      "attributes": {
        "employee": 2116366,
        "date": "1985-03-19",
        "start_time": "10:30",
        "end_time": "22:00",
        "break": 120,
        "comment": "just a couple more parentheses...",
        "is_holiday": false,
        "is_on_time_off": false
      }
    }, {
      "id": 33479602,
      "type": "AttendancePeriod",
      "attributes": {
        "employee": 2116366,
        "date": "1985-03-18",
        "start_time": "10:00",
        "end_time": "20:00",
        "break": 90,
        "comment": "working on GNU Emacs",
        "is_holiday": false,
        "is_on_time_off": false
      }
    }
  ]
}
"""
json_dict_attendance_rms = json.loads(json_string_attendance_rms)

json_string_absence_alan = """
{
  "success": true,
     "metadata":{
        "current_page":1,
        "total_pages":1
   },
  "data": [{
      "type": "TimeOffPeriod",
      "attributes": {
        "id": 17205942,
        "status": "approved",
        "comment": "marathon starts at noon",
        "start_date": "1944-09-01T00:00:00+02:00",
        "end_date": "1944-09-01T00:00:00+02:00",
        "days_count": 0.5,
        "half_day_start": 0,
        "half_day_end": 1,
        "time_off_type": {
          "type": "TimeOffType",
          "attributes": {
            "id": 195824,
            "name": "vacation",
            "category": "vacation"
          }
        },
        "employee": {
          "type": "Employee",
          "attributes": {
            "id": {
              "label": "ID",
              "value": 2116365
            },
            "first_name": {
              "label": "First name",
              "value": "Alan"
            },
            "last_name": {
              "label": "Last name",
              "value": "Turing"
            },
            "email": {
              "label": "Email",
              "value": "alan@example.org"
            }
          }
        },
        "created_by": "Alan Turing",
        "certificate": {
          "status": "not-required"
        },
        "created_at": "2020-08-21T18:07:06+02:00",
        "updated_at": "2021-01-17T10:32:18+01:00"
      }
    }, {
      "type": "TimeOffPeriod",
      "attributes": {
        "id": 17205932,
        "status": "approved",
        "comment": "don't you just hate mondays sometimes?",
        "start_date": "1944-07-03T00:00:00+02:00",
        "end_date": "1944-07-03T00:00:00+02:00",
        "days_count": 1,
        "half_day_start": 0,
        "half_day_end": 0,
        "time_off_type": {
          "type": "TimeOffType",
          "attributes": {
            "id": 195824,
            "name": "vacation",
            "category": "vacation"
          }
        },
        "employee": {
          "type": "Employee",
          "attributes": {
            "id": {
              "label": "ID",
              "value": 2116365
            },
            "first_name": {
              "label": "First name",
              "value": "Alan"
            },
            "last_name": {
              "label": "Last name",
              "value": "Turing"
            },
            "email": {
              "label": "Email",
              "value": "alan@example.org"
            }
          }
        },
        "created_by": "Alan Turing",
        "certificate": {
          "status": "not-required"
        },
        "created_at": "2020-08-21T18:06:02+02:00",
        "updated_at": "2021-01-17T11:32:18+01:00"
      }
    }, {
      "type": "TimeOffPeriod",
      "attributes": {
        "id": 17205920,
        "status": "approved",
        "comment": "summer vacation",
        "start_date": "1944-08-07T00:00:00+02:00",
        "end_date": "1944-08-20T00:00:00+02:00",
        "days_count": 10,
        "half_day_start": 0,
        "half_day_end": 0,
        "time_off_type": {
          "type": "TimeOffType",
          "attributes": {
            "id": 195824,
            "name": "vacation",
            "type": "vacation"
          }
        },
        "employee": {
          "type": "Employee",
          "attributes": {
            "id": {
              "label": "ID",
              "value": 2116365
            },
            "first_name": {
              "label": "First name",
              "value": "Alan"
            },
            "last_name": {
              "label": "Last name",
              "value": "Turing"
            },
            "email": {
              "label": "Email",
              "value": "alan@example.org"
            }
          }
        },
        "created_by": "Alan Turing",
        "certificate": {
          "status": "not-required"
        },
        "created_at": "2020-08-21T18:05:04+02:00",
        "updated_at": "2021-01-18T10:32:18+01:00"
      }
    }
  ]
}
"""
json_dict_absence_alan = json.loads(json_string_absence_alan)

json_string_absence_alan_single = """
{
 "success": true,
    "metadata":{
        "current_page":1,
        "total_pages":1
   },
  "data": [{
      "type": "TimeOffPeriod",
      "attributes": {
        "id": 17205942,
        "status": "approved",
        "comment": "marathon starts at noon",
        "start_date": "1944-09-01T00:00:00+02:00",
        "end_date": "1944-09-01T00:00:00+02:00",
        "days_count": 0.5,
        "half_day_start": 0,
        "half_day_end": 1,
        "time_off_type": {
          "type": "TimeOffType",
          "attributes": {
            "id": 195824,
            "name": "vacation",
            "category": "vacation"
          }
        },
        "employee": {
          "type": "Employee",
          "attributes": {
            "id": {
              "label": "ID",
              "value": 2116365
            },
            "first_name": {
              "label": "First name",
              "value": "Alan"
            },
            "last_name": {
              "label": "Last name",
              "value": "Turing"
            },
            "email": {
              "label": "Email",
              "value": "alan@example.org"
            }
          }
        },
        "created_by": "Alan Turing",
        "certificate": {
          "status": "not-required"
        },
        "created_at": "2020-08-21T18:07:06+02:00",
        "updated_at": "2021-02-17T10:32:18+01:00"
      }
    }
    ]
}
"""
json_dict_absence_alan_first = json.loads(json_string_absence_alan_single)

json_string_absence_types = """
{
  "success": true,
     "metadata":{
        "current_page":1,
        "total_pages":1
   },
  "data": [{
      "type": "TimeOffType",
      "attributes": {
        "id": 195824,
        "name": "vacation",
        "category": "vacation"
      }
    }, {
      "type": "TimeOffType",
      "attributes": {
        "id": 195825,
        "name": "paid leave",
        "category": "paid leave"
      }
    }, {
      "type": "TimeOffType",
      "attributes": {
        "id": 195826,
        "name": "sick",
        "category": "sick"
      }
    }
  ]
}
"""
json_dict_absence_types = json.loads(json_string_absence_types)

json_string_delete_absence = """
{
    "success": true,
       "metadata":{
        "current_page":1,
        "total_pages":1
   },
    "data": {
        "message": "The absence period was deleted."
    }
}
"""
json_dict_delete_absence = json.loads(json_string_delete_absence)

json_string_absence_create_no_halfdays = """
{
   "success":true,
      "metadata":{
        "current_page":1,
        "total_pages":1
   },
   "data":{
      "type":"TimeOffPeriod",
      "attributes":{
         "id":22809350,
         "status":"approved",
         "comment":"",
         "start_date":"2021-01-01T00:00:00+01:00",
         "end_date":"2021-01-10T00:00:00+01:00",
         "days_count":5,
         "half_day_start":1,
         "half_day_end":1,
         "time_off_type":{
            "type":"TimeOffType",
            "attributes":{
               "id":243402,
               "name": "Unpaid vacation",
               "category": "unpaid_vacation"
            }
         },
         "employee":{
            "type":"Employee",
            "attributes":{
               "id":{
                  "label":"ID",
                  "value":2628890
               },
               "first_name":{
                  "label":"First name",
                  "value":"Alan"
               },
               "last_name":{
                  "label":"Last name",
                  "value":"Turing"
               },
               "email":{
                  "label":"Email",
                  "value":"alan.turing@cetitec.com"
               }
            }
         },
         "created_by":"API",
         "certificate":{
            "status":"not-required"
         },
         "created_at": "2020-12-01T18:24:11+01:00",
         "updated_at": "2021-04-17T10:32:18+01:00"
      }
   }
}
"""
json_dict_absence_create_no_halfdays = json.loads(json_string_absence_create_no_halfdays)

json_string_get_absence = """
{
   "success":true,
   "metadata":{
        "current_page":1,
        "total_pages":1
   },
   "data":{
      "type":"TimeOffPeriod",
      "attributes":{
         "id":2628890,
         "status":"approved",
         "comment":"",
         "start_date":"2021-01-01T00:00:00+01:00",
         "end_date":"2021-01-10T00:00:00+01:00",
         "days_count":5,
         "half_day_start":0,
         "half_day_end":1,
         "time_off_type":{
            "type":"TimeOffType",
            "attributes":{
               "id":243402,
               "name":"Unpaid vacation",
               "category":"unpaid_vacation"
            }
         },
         "employee":{
            "type":"Employee",
            "attributes":{
               "id":{
                  "label":"ID",
                  "value":2628890
               },
               "first_name":{
                  "label":"First name",
                  "value":"Alan"
               },
               "last_name":{
                  "label":"Last name",
                  "value":"Turing"
               },
               "email":{
                  "label":"Email",
                  "value":"alan.turing@cetitec.com"
               }
            }
         },
         "created_by":"API",
         "certificate":{
            "status":"not-required"
         },
         "created_at": "2020-12-02T17:28:34+01:00",
         "updated_at": "2022-04-17T10:32:18+01:00"
      }
   }
}"""
json_dict_get_absence = json.loads(json_string_get_absence)

json_string_attendance_create_no_break = """
{
   "success":true,
   "data":{
      "id": [83648700],
      "message": "success"
   }
}
"""
json_dict_attendance_create_no_break = json.loads(json_string_attendance_create_no_break)

json_string_attendance_patch = """
{
   "success":true,
   "data":{
      "message": "success"
   }
}
"""
json_dict_attendance_patch = json.loads(json_string_attendance_patch)

json_string_attendance_delete = """
{
   "success":true,
   "data":{
      "message": "success"
   }
}
"""
json_dict_attendance_delete = json.loads(json_string_attendance_delete)

json_string_project_rms = """
{
  "success": true,
  "data": [
    {
      "id": 238751,
      "type": "Project",
      "attributes": {
        "name": "conwik project",
        "active": true,
        "created_at": "2019-03-01T16:00:00",
        "updated_at": "2020-03-02T16:11:35"
      }
    }, {
      "id": 238750,
      "type": "Project",
      "attributes": {
        "name": "mock project",
        "active": true,
        "created_at": "2023-03-28T16:11:35",
        "updated_at": "2023-03-28T16:11:35"
      }
    }, {
      "id": 238752,
      "type": "Project",
      "attributes": {
        "name": "alianz project",
        "active": false,
        "created_at": "2020-10-10T10:11:35",
        "updated_at": "2023-02-22T17:11:35"
      }
    }
    ]
}
"""
json_dict_project_rms = json.loads(json_string_project_rms)

json_string_project_create = """
{
  "success":true,
   "data":{
      "id": 83648600,
      "message": "success"
   }
}
"""
json_dict_project_create = json.loads(json_string_project_create)

json_string_project_delete = """
{
   "text":"",
   "status_code": 204
}
"""
json_dict_project_delete = json.loads(json_string_project_delete)

json_string_project_update = """
{
  "success": true,
  "data": {
      "id": 238760,
      "type": "Project",
      "attributes": {
        "name": "updated mock project",
        "active": true,
        "created_at": "2023-03-28T16:11:35",
        "updated_at": "2023-03-28T16:11:52"
      }
    }
}
"""
json_dict_project_update = json.loads(json_string_project_update)

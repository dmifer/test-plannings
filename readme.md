# Planning creation. Test task

Hello! :)

In this repository you can find a function used in planning process for plannings objects creation, setting approvals and sending email notifications.

Please refer to the file `create_plannings.py`

We are using MongoDB as database, you can use the cloud one or run it in Docker locally. `data_examples` folder contains data sample you need to injest into DB.

Payload example:

```
[
    {
        "id": 1698180320006.1234,
        "_id": null,
        "user": "ivan.ivanov@company.com",
        "name": "Ivan Ivanov",
        "client": "LAB",
        "project": "LAB_PROJECT_1",
        "task": null,
        "dayStart": "22.05.2023",
        "dayFinish": "24.05.2023",
        "hours": 24,
        "type": "add",
        "daily_hours": [8, 8, 8],
        "distributed": false,
        "detailed_hours": {
            "22.05.2023": 8,
            "23.05.2023": 8,
            "24.05.2023": 8
        },
        "virtual": true,
        "non_working_days": []
    },
    {
        "id": 1698180320006.1414,
        "_id": null,
        "user": "ivan.ivanov@company.com",
        "name": "Ivan Ivanov",
        "client": "LAB",
        "project": "LAB_PROJECT_1",
        "task": null,
        "dayStart": "22.05.2023",
        "dayFinish": "24.05.2023",
        "hours": 12,
        "type": "add",
        "daily_hours": [4, 4, 4],
        "distributed": false,
        "detailed_hours": {
            "22.05.2023": 4,
            "23.05.2023": 4,
            "24.05.2023": 4
        },
        "virtual": true,
        "non_working_days": []
    },
    {
        "id": 1698180344313.8406,
        "_id": null,
        "user": "ivan.ivanov@company.com",
        "name": "Ivan Ivanov",
        "client": "LAB",
        "project": "LAB_PROJECT_1",
        "task": null,
        "dayStart": "25.05.2023",
        "dayFinish": "26.05.2023",
        "hours": 10,
        "daily_hours": [8, 2],
        "detailed_hours": {
            "25.05.2023": 8,
            "26.05.2023": 2
        },
        "type": "add",
        "distributed": true,
        "virtual": true,
        "non_working_days": []
    }
]

```


### Tasks

This function will be used as base for you technical tasks:
1. Create a fork of this repo
2. Understand the logic of the function
3. Review and refactor it
4. Push commit(s) to the for repository with the explanation
5. Fill in section below with short description of changes you've made


### Changes made

- I added the `.getignore` file, for excluding local files like the `venv` (Python virtual environment) folde.

- I added the `.env` file that contains configuration values that may differ based on whether the application is running locally or on a production.

- I converted the function names from `camel case` to `snake case`,
  following Python's recommended naming convention.

- I used **Dependency Injection** to inject the database instead of accessing it directly in the code. This approach is highly beneficial, especially when writing **tests**.

- I created a new file named `planning_crud.py` and transferred all the database operations to it.

- I refactored the code to make it simpler, more maintainable, and less prone to bugs. I ensured adherence to standard Python coding guidelines following **PEP 8**.

- I aimed to adhere to the **Single Responsibility Principle**, so I refactoried functions that previously had multiple responsibilities into a list of simpler, more understandable functions.

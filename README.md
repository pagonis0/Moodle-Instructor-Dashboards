# THISuccess^AI Instructor Dashboard Graphical Analyis



## Description

This service provides via an API call an object which could be used directly from the Moodle sytsem to produce Graphics for the dashboard of the instructors. The graphs are dedicated to provide information on the professors for their courses and their students. All the provided graphics are for each course individually and do not provid overall information.
The currently exist object will be used to generate a graphical analysis of the usage of the material provided in each course, as well as the preparation before the lecture (using the dedicated to the lecture material) and the postprocessing of the lectures. The object is callable only through an API given specific parameters.
In the future on more graphic for student score on the material given will be provided and on that point more infromation will be explained.



## Installation

As it is part of the main setup of success-ai server the Installation process is the same as described there.

## Components
### Usage Graphics

The class methods performs data processing in way to create a ready to use objectfor the Moodle system with all the needed information to generate a graph of the usage of Learning Nuggets of each course. The Methods of the class give the opportunity to filter the data using Learning Nugget ID, course, a date range, chapters of the course and even the lecture dates.

## Call the service

In order to call the service you need to have access the the Bearer token.
Afterwards you just have to give the input parameters and the response will be printed.
```
{
  "courseid": 32,
  "date_range": ["21.12.2023", "02.12.2024"],
  "LN": ["*"]
}
```

## Example Result
The example result contains only one object id.
In Moodle it could be used to provide the date to x-Axis, the object id for the stacked bars and into the object the count_user_id or count_unique_user_id can provide the y-Axis.
```
{
    "21-12-2023": {
        "269": {
            "courseid": 32,
            "coursename": "Mathematik 1 WS 23/24",
            "lectureDate": [
                "1970-01-01"
            ],
            "membersInCourse": 122.0,
            "nuggetName": [
                "Eigenschaften von Funktionen (Aufg. mittel)"
            ],
            "count_user_id": 1,
            "count_unique_user_id": 1
        }
    }
}
```



## Update Schedule

- Users to be removed as needed based on new team members or professors

## Version Control

Current version is 1.0
The service will updated soon with new filters and graphs

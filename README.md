# spire-api.melanson.dev

An API for public information on [UMass Spire](https://www.spire.umass.edu/).

## Purpose

Information about courses, sections, and subjects is publicly available; but retrieving that information from Spire is difficult. To enable myself, and other students, to create applications that work with this data I created a web crawler to retrieve as much information from Spire as possible.

## Documentation

A list of schemas and endpoints can be found [here](https://spire-api.melanson.dev/docs).

## Crawling Routine

As of October 2023:

-   Academic Calendar: Once a week
-   Courses: Once every two weeks
-   Sections (quick): Once a week

**Requests to endpoints do not immediately query Spire and get the most up-to-date information.** Requests will query a database that is routinely updated. This means that the information in this database is not guaranteed to be accurate.

`Section` and `Course` records have an included `_updated_at` field which document when their information was last updated.

The crawler implements a "quick scrape" feature, that will scrape section information from the search results and avoid having to visit the sections page. A section will be scraped if one of the following is true:

-   Section does not exist in database
-   Section is combined with another section
-   Section status (open, closed, wait-listed) is different from what is stored
-   Section enrollment total (# of students in enrolled in a course) is different from what is stored
-   Section enrollment capacity (# of students allowed to enroll) is different from what is stored

### Coverage

Every course (and subject) in the course catalog ("Browse Course Catalog") is scraped.

Every section during or after the Fall 2018 term is scraped. But only sections that will reasonably be updated are scraped routinely. Meaning, once posted, terms are scraped routinely until they are considered over (Spring ends in June 1st, Summer ends in September 15th, Fall ends in January 1st, Winter ends in February 15th).

## Inconsistencies

Instructor names are assumed to be unique. This makes handling cases where staff names are documented without emails nicer to handle. This does come with the drawback that some staff members might be merged together (considered the same person despite having different emails). However, I do not think that this will happen frequently and the benefit of matching sections labeled without an email is outweighs this.

## Organization

A `Course` is a unique instance of an ID across spire. The default information for a course is first obtained from the course catalog. This will generate structures like a `CourseDetail` and `CourseEnrollmentInformation` based on the present information on a course's catalog page.

A `CorseOffering` is an offering of a course during a specific semester. The course offerings will map to their matching `Course` via ID. Offerings may list different titles than what was originally found for the course. Thus, `CourseOfferings` may potentially have an `alternative_title` field.

Within that offering, will be a list of `Section`s. If a section is found that references a course that was not listed in the course catalog, then a stub `Course` object is created (without any `CourseDetail` or `CourseEnrollment` information objects).



# Building a Graph

A SCTA compliant graph must include a reference to the scta context file.

```json
{
  "@context": "http://scta.info/api/core/1.0/people/context.json",
}
```

or

```json
{
  "@context": "https://raw.githubusercontent.com/scta/scta-people/master/context.json",
}
```

The SCTA context file describes the available vocabularies and property values allowed within a SCTA compliant graph.

## Basic Stum Record
A basic "stub" record looks as follows

```json
{
  "@context": "http://scta.info/api/core/1.0/people/context.json",
  "@id": "sctar:Aquinas",
  "@type": "sctar:person",
  "dc:title": "Thomas Aquinas", //should this be rdfs:label instead of dc:title
  "sctap:shortId": "Aquinas",
  "sctap:numberID": 100000,
  "owl:sameAs": [
     "http://dbpedia.org/resource/Thomas_Aquinas"
  ]
}  
```
## Names, Aliases, and Name Languages

While the stub record offers a default label, a medieval name can have many forms in many different langugages.

A medieval person may have several names appear in several different languages.

For a name we use http://schema.org/name or schema:name

For alias we use http://schema.org/alternateName or schema:alternateName

Each name or alternateName can take a literal as a direct value, for example:

```json
"schema:name": "Thomas Aquinas"
```
or an object declaring the language type, for example:

```json
"schema:name":
  {
    "@value": "Thomas Aquinas",
    "@language": "en"
  }
```

or an array of objects containing the same name in multiple langagues, for example

```json
"schema:name":
  {
    "@value": "Thomas Aquinas",
    "@language": "en"
  }
  {
    "@value": "Thomas von Aquin",
    "@language": "de"
  }
```

Reconciliation Policy:

The SCTA will always aim to record a single name record for a person resource, but will support the collection of multiple alias.

Name entries within the scta graph will be considered to have a first priority. Linked graphs will be crawled, and if an identical string value for a name in a given language, further information can be collected from this feed and appended to the record.

Otherwise, such names will be appended as schema:alternativeName

Overtime, certain variation forms of names will emerge. These will be added to a name entry, and will serve to black list these variations from being added as alternativeName.

For example, an external feed might offer a name for Thomas Aquinas like:

```json
"schema:name":
  {
    "@value": "Saint Thomas Aquinas",
    "@language": "en"
  }
```
or
```json
"schema:name":
  {
    "@value": "Thomas of Aquinas",
    "@language": "en"
  }
```

These are neither alternative names nor the same name in a different language.

During aggregation, these names will initially got logged as schema:alternativeName. As they are recognized as variations, they will get appended to the name entry as a "variation", like so:

```json
"schema:name":
  {
    "@value": "Thomas Aquinas",
    "@language": "en",
    "sctap:nameVaration": "St. Thomas Aquinas"
  }
```

 These variations will effecitvely blacklist the aggregator from ever adding this value as an alternativeName.


## Relationships

http://xmlns.com/foaf/spec/

## Classifcations

### sctap:personType

Possible values include:
* scholastic
* classical
* patristic

### sctap:clericalStatus:
Possible values include:
* secular
* dominican
* franciscan
* augustinian
* carmelite
* benedictine

## Events

http://motools.sourceforge.net/timeline/timeline.html
http://motools.sourceforge.net/event/event.html

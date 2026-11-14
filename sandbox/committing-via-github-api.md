# Syncing and Committing to SCTA-people via the Github api

When a user requests an existing Person entry to update, your application should pull or request the matching Person record from the master branch of the SCTA-People directory. If the path is not already known to your application, it can be retrieved by querying SCTA database, and the SCTA core API.

After the record is updated, whatever else your application chooses to do with the new data, it should produce a new record according to the SCTA people guidelines. (Listed properties for a record should always be in alphabetical order. This will help reduce unnecessary changes in the git history due to re-arranged properties.)

Your application should then do two things.

First, it should, using the Github API, commit the new file either to a SCTA-People branch dedicated to your application or commit to a fork of the SCTA-People repository maintained by you.

Second, again using the github api, your application should submit a pull request, requesting that the updated record be merged into the master repository.

Below are examples of the three main stages an application must perform. The examples are written below using cURL, but can be easily translated into most modern programming languages.

More information on using the github api can be found at [https://developer.github.com/v3/](https://developer.github.com/v3/).

## Syncing

Using the known location of the record in question, the file contents can be requested.

```json

curl https://api.github.com/repos/scta/scta-people/contents/graphs/Aquinas.jsonld
{
  "name": "Aquinas.jsonld",
  "path": "graphs/Aquinas.jsonld",
  "sha": "fbce3f79be6043ed558d2740e76991eb04bb3ac9",
  "size": 361,
  "url": "https://api.github.com/repos/scta/scta-people/contents/graphs/Aquinas.jsonld?ref=master",
  "html_url": "https://github.com/scta/scta-people/blob/master/graphs/Aquinas.jsonld",
  "git_url": "https://api.github.com/repos/scta/scta-people/git/blobs/fbce3f79be6043ed558d2740e76991eb04bb3ac9",
  "download_url": "https://raw.githubusercontent.com/scta/scta-people/master/graphs/Aquinas.jsonld",
  "type": "file",
  "content": "ewogICJAY29udGV4dCI6ICJodHRwOi8vc2N0YS5pbmZvL2FwaS9jb3JlLzEu\nMC9wZW9wbGUvY29udGV4dC5qc29uIiwKICAiQGlkIjogImh0dHA6Ly9zY3Rh\nLmluZm8vcmVzb3VyY2UvQXF1aW5hcyIsCiAgIkB0eXBlIjogImh0dHA6Ly9z\nY3RhLmluZm8vcmVzb3VyY2UvcGVyc29uIiwKICAiZGM6dGl0bGUiOiAiVGhv\nbWFzIEFxdWluYXMiLAogICJzY3RhcDpwZXJzb25UeXBlIjogImh0dHA6Ly9z\nY3RhLmluZm8vcmVzb3VyY2Uvc2Nob2xhc3RpYyIsCiAgInNjdGFwOnNob3J0\nSWQiOiAiQXF1aW5hcyIsCiAgIm93bDpzYW1lQXMiOiBbCiAgICAiaHR0cDov\nL2RicGVkaWEub3JnL3Jlc291cmNlL1Rob21hc19BcXVpbmFzIgogIF0KICAK\nfQ==\n",
  "encoding": "base64",
  "_links": {
    "self": "https://api.github.com/repos/scta/scta-people/contents/graphs/Aquinas.jsonld?ref=master",
    "git": "https://api.github.com/repos/scta/scta-people/git/blobs/fbce3f79be6043ed558d2740e76991eb04bb3ac9",
    "html": "https://github.com/scta/scta-people/blob/master/graphs/Aquinas.jsonld"
  }
}
```

The value of `content` key contains the record encoded in base64. To parse it, your application will need to de-encode it. Then your application offer to the user, the information already known, and offer them a chance to add or correct a field.

## Committing

When a user is "saving" their modifications and updates, your application will need to construct re-encode the updated content in base64, and then construct a "commit" payload that looks like the following.

```json
{
  "message": "my test commit message",
  "committer": {
    "name": "Jeffrey C. Witt",
    "email": "jeffreycwitt@gmail.com"
  },
  "content": "[updated base64 encoded content]",
  "sha": "fbce3f79be6043ed558d2740e76991eb04bb3ac9",
  "branch": "yourbranch"
}
```

The "sha" property asks of the hash of the current state of the file you aim to update. This sha was provided to your application above when you requested the content via the github api.

If you are submitting to an official branch set up for your application, the branch name will need to correspond to the branch to which your application has write access. If you are submitting to your own fork, the branch name will likely be "master"

Finally you will need to submit a post request. The example below in curl uses basic auth, but your application should use Github OAuth protocol. Again if you are submitting a branch on the official SCTA-People repository, you will need Auth Token from the SCTA-People maintainers.

`curl --user jeffreycwitt -X PUT -H "Accept: application/json" -H "Content-type: application/json" -d "[the data to be posted or a file reference containing the data]" https://api.github.com/repos/scta/scta-people/contents/graphs/Aquinas.jsonld`

## Submitting a Pull Request

Finally your application will need to submit a pull request as follows:

First it will need to create a payload:

If your commit was to forked repository, it needs to look like this:
```json
{
  "title": "Aquinas Record Updated",
  "body": "Please pull this in!",
  "head": "your-account-name:branch-of-update-record",
  "base": "master"
}
```

If you are working with a branch within the SCTA-People repository it should look as follows

```json
{
  "title": "Aquinas Record Updated",
  "body": "Please pull this in!",
  "head": "branch-of-update-record",
  "base": "master"
}
```
`curl --user jeffreycwitt -X PUT -H "Accept: application/json" -H "Content-type: application/json" -d '{ "title": "Aquinas Record Updated","body": "Please pull this in!","head": "public","base": "master"}' https://api.github.com/repos/scta/scta-people/pulls`

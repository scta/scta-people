var fs = require("fs");
var path = require("path");
var axios = require("axios");
var moment = require("moment");



fs.readdir("../graphs/", (err, files) => {

  //clear xml supplment file
  fs.writeFile('../ProsopographySupplement.xml', '', function(){console.log('done')});
  // add xml header
  var stream = fs.createWriteStream("../ProsopographySupplement.xml", {flags:'a'});
    stream.write('<?xml version="1.0" encoding="UTF-8"?>\n<persons>\n');
  stream.end();

  files.forEach ((file, index) => {
    const rawdata = fs.readFileSync("../graphs/" + file);
    const jsondata = JSON.parse(rawdata);



    if (jsondata["owl:sameAs"]){
      jsondata["owl:sameAs"].forEach((d)=>{
        if (d.includes("https://www.wikidata.org/")){
          axios.get(d, {
            headers: {'Content-Type': 'application/json'}
          }).then((data) => {
            let description = undefined;
            if (data.data.entities[Object.keys(data.data.entities)[0]].descriptions){
              description = data.data.entities[Object.keys(data.data.entities)[0]].descriptions.en.value;
              console.log("description", description );
            }
            let label = undefined
            if (data.data.entities[Object.keys(data.data.entities)[0]].labels){
              label = data.data.entities[Object.keys(data.data.entities)[0]].labels.en.value
              console.log("label", label);
            }
            let birthdate = undefined
            if(data.data.entities[Object.keys(data.data.entities)[0]].claims.P569){
              birthdate = data.data.entities[Object.keys(data.data.entities)[0]].claims.P569[0].mainsnak.datavalue.value.time;
              console.log("birthdate", birthdate);
            }
            let deathdate = undefined
            if(data.data.entities[Object.keys(data.data.entities)[0]].claims.P570){
              deathdate = data.data.entities[Object.keys(data.data.entities)[0]].claims.P570[0].mainsnak.datavalue.value.time;
              console.log("deathdate", deathdate);
            }
            let orderid = undefined
            if (data.data.entities[Object.keys(data.data.entities)[0]].claims.P611){
              orderid = data.data.entities[Object.keys(data.data.entities)[0]].claims.P611[0].mainsnak.datavalue.value.id
              }
            if (orderid){
              getOrderLabel(orderid).then((data) => {
                finalobject = {
                  "label": label,
                  "description": description,
                  "dateofbirth": birthdate,
                  "dateofdeath": deathdate,
                  "order_label": data
                }
                const newjson = {
                  ...jsondata,
                  ...finalobject
                }
                //console.log(newjson)
                writeTofile(file, newjson)
              }).catch(console.log("error"))
            }
            else{
              finalobject = {
                "label": label,
                "description": description,
                "dateofbirth": birthdate,
                "dateofdeath": deathdate
              }
              const newjson = {
                ...jsondata,
                ...finalobject
              }
              console.log(newjson)
              console.log("dateofbirth", newjson.dateofbirth)
              console.log("dateofdeath", newjson.dateofdeath)

              writeTofile(file, newjson)

            }
          });
        }
      });
    }

  });

});

function getOrderLabel(orderid){
  console.log("orderid", orderid);
  let promiseObject = axios.get("https://www.wikidata.org/wiki/Special:EntityData/" + orderid + ".json", {
    headers: {'Content-Type': 'application/json'}
  }).then((newdata) => {
      order_label = newdata.data.entities[Object.keys(newdata.data.entities)[0]].labels.en.value;
      console.log("order label", order_label);
      return order_label

  }).catch(console.log("error"));
  return promiseObject
}

function writeTofile(file, newjson){
  writeXMLfile(newjson);

  fs.writeFile("../build/" + file, JSON.stringify(newjson, null, 2), 'utf8', function(err){
    if (err){
      return console.log(err);
    }
  });
}

function writeXMLfile(newjson){
  const birthDate = newjson.dateofbirth.substring(1, 5)
  const deathDate = newjson.dateofdeath.substring(1, 5)
  var stream = fs.createWriteStream("../ProsopographySupplement.xml", {flags:'a'});
  stream.write("<person>\n<shortId>" + newjson["sctap:shortId"] + "</shortId>\n<dateofbirth>" + birthDate + "</dateofbirth>\n<dateofdeath>" + deathDate + "</dateofdeath>\n<description>" + newjson.description + "</description>\n</person>\n");
  stream.end();
}

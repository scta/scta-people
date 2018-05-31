var fs = require("fs");
var path = require("path");
var axios = require("axios");
var moment = require("moment");



fs.readdir("../graphs/", (err, files) => {

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
                  "order_label": data
                }
                const newjson = {
                  ...jsondata,
                  ...finalobject
                }
                console.log(newjson)
                writeTofile(file, newjson)
              }).catch(console.log("error"))
            }
            else{
              finalobject = {
                "label": label,
                "description": description,
                "dateofbirth": birthdate,
              }
              const newjson = {
                ...jsondata,
                ...finalobject
              }
              console.log(newjson)
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
  fs.writeFile("../build/" + file, JSON.stringify(newjson, null, 2), 'utf8', function(err){
    if (err){
      return console.log(err);
    }
  });
}

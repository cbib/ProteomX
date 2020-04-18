'use strict';

const fs = require('fs');
const path = require('path')
const   bodyParser = require('body-parser');
const   cors = require('cors');
const express = require('express')
const config = require('config');
const XLSX = require('xlsx')
const { exec } = require("child_process");
const uuid = require('uuid-random');
const {spawnSync} = require('child_process');
const {spawn} = require('child_process');
var app = express();
app.use(express.json({limit: '50mb'}));
app.use(express.urlencoded({extended: false, limit: '50mb'}));
app.use(cors());
const data_folder=config.get("data_folder");


let appPort = config.get('api_server.port');
app.listen(appPort, () => {
 console.log("Server running on port ${appPort}");
});

//run python script
app.get('/headers', callName);

function callName(req, res) {
    console.log("Received request for call name ")
    
    // Use child_process.spawn method from
    // child_process module and assign it
    // to variable spawn
    var spawn = require("child_process").spawn;
    var process = spawn('python',[config.get("helloworld_script")]);
    console.log(`Spawned subprocess at  ${config.get("helloworld_script")}`)
    
    // Takes stdout data from script which executed
    // with arguments and send this data to res object
    process.stdout.on('data', function(data) {
        res.send(data.toString());
    })
}


app.post("/upload", (req, res, next) => {
    //const {spawnSync} = require('child_process');
    //var exec = require("child_process").exec;
    var original_filename=req.body.filename;
    var book=req.body.book;
    //generate unique random uuid
    var unique_id=uuid();
    var errors=[]
    
    //create project_repository using uuid
    //var mkdir_command="mkdir "+data_folder+"/"+unique_id;
    //console.log(mkdir_command)
    //const mkdir_process=spawn(mkdir_command)
  
    fs.mkdirSync(data_folder+"/"+unique_id, { recursive: true }, (err) => {
    if (err) throw err;
    });
    //const subprocessinit=spawnSync(mkdir_command);
    //console.log(subprocessinit.stdout.toString());
    
    
    var configfilename= data_folder+"/config_files/config_file.json"
    var errorfilename= data_folder+"/"+unique_id+"/check_and_export_to_csv_error.json"
    var csvfilename= data_folder+"/"+unique_id+"/"+original_filename+".csv"
    var samplefilename= data_folder+"/"+unique_id+"/sample_name.json"
    var filename= data_folder+"/"+unique_id+"/"+original_filename+".xlsx"
    
//    var configfilename= data_folder+"/config_files/config_file.json"
//    var errorfilename= data_folder+"/"+unique_id+"_check_and_export_to_csv_error.json"
//    var csvfilename= data_folder+"/"+unique_id+"_"+original_filename+".csv"
//    var samplefilename= data_folder+"/"+unique_id+"_sample_name.json"
//    var filename= data_folder+"/"+unique_id+"_"+original_filename+".xlsx"
    
    
    XLSX.writeFile(book,filename);
    //here call check_and_export_to_csv.py inplace
    var args_list=[config.get("check_and_export_to_csv_script"), "-i", filename,"-c",configfilename,"-er" ,errorfilename,"-o",csvfilename,"-s",samplefilename]
    function runPythonScript(args_l){
        
        return spawnSync('python', args_l);
    }
    const subprocess = runPythonScript(args_list);
    
    //console.log(subprocess.stdout.toString())
    //fs.writeFileSync(errorfilename, JSON.stringify(req.body.associated_headers));
    var data_sample_name =fs.readFileSync(samplefilename);
    var error =fs.readFileSync(errorfilename);
    //console.log(JSON.stringify(data))
    res.send({error: error.toString(), uuid:unique_id, data_sample_name: data_sample_name.toString()});

    //res.send({associated_headers: req.body.associated_headers, uuid:unique_id, sample_name: JSON.stringify(sample_name)});

});




// This function use spawnSync that allows to wait for script to finish.
// Output json file is read in Sync mode and content is returned.
app.get('/get_headers/', (req, res) => {
    var file_uuid=req.query.file_uuid;
    const {spawnSync} = require('child_process');
    const path = require('path');
    function runScript(){
        return spawnSync('python', ["/Users/benjamin/hello.py"
        ]);
    }
    const subprocess = runScript();
    var data =fs.readFileSync("/Users/benjamin/"+file_uuid+".json");
    //console.log(data.toString());
    // print output of script
    res.send(data.toString());
    //res.send(subprocess.stdout.toString());
});







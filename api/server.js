'use strict';

const fs = require('fs');
//const express = require('express')
const path = require('path')
const   bodyParser = require('body-parser');
const   cors = require('cors');
////const    mongoose = require('mongoose'),
//exec = require("child_process").exec;
//
//const app = express();
////let port = process.env.PORT || 3000;
//
//const server = app.listen(function(){
//    console.log('Listening on port ' + port);
//});
const { exec } = require("child_process");

exec("ls -la", (error, stdout, stderr) => {
    if (error) {
        console.log(`error: ${error.message}`);
        return;
    }
    if (stderr) {
        console.log(`stderr: ${stderr}`);
        return;
    }
    console.log(`stdout: ${stdout}`);
});
var XLSX = require('xlsx')
var express = require("express");
//exec = require("child_process").exec;
//spawn = require("child_process").spawn;
//const { spawn } = require('child_process');

//const child = spawn('ls');

var app = express();
//app.use(bodyParser.urlencoded({ extended: false}));
//app.use(bodyParser.json({limit: '50mb'}));
app.use(express.json({limit: '50mb'}));
app.use(express.urlencoded({extended: false, limit: '50mb'}));
app.use(cors());

//app.use(express.json({limit: '50mb'}));
//sapp.use(express.urlencoded({limit: '50mb'}));
app.listen(4000, () => {
 console.log("Server running on port 4000");
});


app.get('/headers', callName); 
  
function callName(req, res) { 
      
    // Use child_process.spawn method from  
    // child_process module and assign it 
    // to variable spawn 
    var spawn = require("child_process").spawn; 
    var process = spawn('python',["/Users/benjamin/hello.py"]); 
    // Takes stdout data from script which executed 
    // with arguments and send this data to res object 
    process.stdout.on('data', function(data) { 
        res.send(data.toString()); 
    } ) 
}


app.post("/upload", (req, res, next) => {
    //var associated_headers=req.associated_headers;
    //var filename = req.filename;
    var book=req.body.book;
    XLSX.writeFile(book, "/Users/benjamin/Excel.xlsx");
    fs.writeFileSync('/Users/benjamin/Excel.json', JSON.stringify(req.body.associated_headers));
    var spawn = require("child_process").spawn; 
    var process = spawn('python',["/Users/benjamin/hello.py"]); 
    //res.send({success:true, message:'Everything is good now ',associated_headers: associated_headers });
    process.stdout.on('data', function(data) { 
        res.json({data:data.toString()}); 
    } );
    
//    res.json({associated_headers:req.body.associated_headers});
    
    
    
});



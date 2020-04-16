import { Component, OnInit } from '@angular/core';
import { DataTablesModule } from 'angular-datatables';
import { FormBuilder, FormGroup } from  '@angular/forms';
import { CdkDragDrop, moveItemInArray} from '@angular/cdk/drag-drop';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA} from '@angular/material/dialog';
import { DelimitorDialogComponent } from '../dialog/delimitor-dialog.component';
import { MiddlewareService} from '../services/middleware.service';
import { AlertService} from '../services/alert.service';
import * as XLSX from 'xlsx';

@Component({
  selector: 'app-download',
  templateUrl: './download.component.html',
  styleUrls: ['./download.component.css']
})
export class DownloadComponent implements OnInit {
    private data ={}
    fileUploaded: File;  
    fileName:string=""
    fileUploadProgress: string = null;
    uploadedFilePath: string = null;
    error: string;
    userId: number = 1;
    storeData:any;
    worksheet: any;
    public selectedGroup:string;
    public modified:boolean=false;
    public form: FormGroup;
    //parsing CSV
    private delimitor:string;
    private csv:any;
    private headers=[];
    private headers_select=[];
    public associated_headers={};
    private lines=[];
    uploadResponse = { status: '', message: 0, filePath: '' };
    
    constructor(public dialog: MatDialog, public alertService: AlertService, private middlewareService: MiddlewareService){
    
     //this.middlewareService.list_directory()
       }
    get_headers(){
        return this.headers
    }
    
    get_associated_headers(){
        return this.associated_headers;
    }
    get_headers_select(){
        return this.headers_select;
    }
    get_lines(){
        return this.lines
    }
    ngOnInit(): void {
        //this.form = this.formBuilder.group({file: ['']});
    }
    drop(event: CdkDragDrop<string[]>) {
        moveItemInArray(this.headers_select, event.previousIndex, event.currentIndex);
        this.modified=true
        console.log(this.headers)
        console.log(this.associated_headers)
    }
//    reset(event){
//        console.log("1#################################################")
//        console.log(event.target)
//    }
    readExcel() {  
        let fileReader = new FileReader();  
        fileReader.onload = (e) => {  
                    this.storeData=fileReader.result;
                    var data = new Uint8Array(this.storeData);  
                    var arr = new Array();  
                    for (var i = 0; i != data.length; ++i) arr[i] = String.fromCharCode(data[i]);  
                    var bstr = arr.join(""); 
                    var book = XLSX.read(bstr, { type: "binary" }); 
                    var first_sheet_name = book.SheetNames[0];  
                    this.worksheet = book.Sheets[first_sheet_name]; 
                    this.csv = XLSX.utils.sheet_to_csv(this.worksheet);  
                    this.load_csv(this.csv,e) ;


        }  
        fileReader.readAsArrayBuffer(this.fileUploaded);  
    }
    onFileChange(event) {
        console.log("1#################################################")
        //this.fileUploaded = <File>event.target.files[0];
        
        
        if (event.target.files.length > 0) {
            
            this.uploadResponse.status='progress'
            this.fileUploaded = event.target.files[0];
            let fileReader = new FileReader();
            this.fileName=this.fileUploaded.name
                
            if (this.fileUploaded.type==="text/csv"){
                const dialogRef = this.dialog.open(DelimitorDialogComponent, {width: '1000px', data: {delimitor: ""}});
                dialogRef.afterClosed().subscribe(data => {
                    console.log(data)
                if (data!==undefined){
                    console.log(data.delimitor)
                    this.delimitor = data.delimitor;
                    console.log(this.delimitor);
                    this.read_csv(this.delimitor) 
                };
            });
                
                
                
                
                
            }
            else{               
                this.readExcel();
                
            }
            //this.loaded=true
            //this.form.get('file').setValue(this.fileUploaded);
            
        }
    }
    
    read_csv(delimitor:string){
        let fileReader = new FileReader();
        fileReader.onload = (e) => {
            this.csv=fileReader.result;
            this.load_csv(this.csv,e,delimitor)
        }
        fileReader.readAsText(this.fileUploaded); 
    }
    
    load_csv(csvData:any,e:any,delimitor:string=","){
        let allTextLines = csvData.split(/\r|\n|\r/);
        this.headers = allTextLines[0].split(delimitor);
        this.lines = [];
        for (let i = 1; i < allTextLines.length; i++) {
            this.uploadResponse.message=Math.round(100* (e.loaded / e.total))
            // split content based on comma
            let data = allTextLines[i].split(',');
            if (data.length === this.headers.length) {
                let tarr = [];
                for (let j = 0; j < this.headers.length; j++) {
                    tarr.push(data[j]);
                }
                this.lines.push(tarr);
            }
        }
        for (var i = 0; i < this.headers.length; i++){
            
            
            this.associated_headers[this.headers[i]]={selected:false,associated_term_id:"",is_time_values:false}
            if (i===0){
                this.headers_select.push('time')
            }
            else{
                this.headers_select.push('others')
            }
            
        }
        console.log(this.associated_headers)
    }
      
    readAsCSV() {  
        var csvData = XLSX.utils.sheet_to_csv(this.worksheet);  
        const data: Blob = new Blob([csvData], { type: 'text/csv;charset=utf-8;' });
          
        //FileSaver.saveAs(data, "CSVFile" + new Date().getTime() + '.csv');  
    }
    onSubmit() {
        console.log(this.lines.length)
        if (this.lines.length!==0){
            //console.log(this.form.get('avatar').value)
            //console.log(this.loaded)
            const formData = new FormData();
            formData.append('file', this.form.get('file').value);
            //let user=JSON.parse(localStorage.getItem('currentUser'));
            //let parent_id="studies/981995"
            //this.uploadService.upload2(this.fileName,this.lines,this.headers,this.associated_headers,this.parent_id).pipe(first()).toPromise().then(data => {console.log(data);})
            //this.router.navigate(['/tree'],{ queryParams: { key: user._key  } });
        }
        else{
            this.alertService.error("you need to select a file")
        }
        
        

        //    this.uploadService.upload(this.lines).subscribe(
        //      (res) => this.uploadResponse = res,
        //      (err) => this.error = err
        //    );
    }
    onSelect(values:string, key:string) {
        
    }

}

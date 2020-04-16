import { Component, OnInit, Input } from '@angular/core';
import { DataTablesModule } from 'angular-datatables';
import { FormBuilder, FormGroup,Validators ,FormArray, FormControl } from  '@angular/forms';
import { Router,ActivatedRoute } from '@angular/router';
import { CdkDragDrop, moveItemInArray} from '@angular/cdk/drag-drop';
import { MatDialog, MatDialogRef, MAT_DIALOG_DATA} from '@angular/material/dialog';
import { DelimitorDialogComponent } from '../dialog/delimitor-dialog.component';
import { MiddlewareService} from '../services/middleware.service';
import { AlertService} from '../services/alert.service';
import * as XLSX from 'xlsx';
import { first } from 'rxjs/operators';

@Component({
  selector: 'app-metadata-description',
  templateUrl: './metadata-description.component.html',
  styleUrls: ['./metadata-description.component.css']
})
export class MetadataDescriptionComponent implements OnInit {
    @Input() associated_headers:{};
    @Input() uuid:string
    private data ={}
    fileUploaded: File;  
    fileName:string=""
    fileUploadProgress: string = null;
    uploadedFilePath: string = null;
    storeData:any;
    worksheet: any;
    book:any;
    public selectedGroup:string;
    public modified:boolean=false;
    public form: FormGroup;
    group1_label_form = new FormControl('');
    group2_label_form = new FormControl('');
    select_form = new FormControl('');
    public group1_label:string= "group1";
    public group2_label:string= "group2";
    public species:string;
    //parsing CSV
    private delimitor:string;
    private csv:any;
    private headers=[];
    private headers_select=[];
    private lines=[];
    uploadResponse = { status: '', message: 0, filePath: '' };
    
    constructor(private route: ActivatedRoute, private router: Router,  public dialog: MatDialog, public alertService: AlertService, private middlewareService: MiddlewareService,private formBuilder: FormBuilder){
     this.route.queryParams.subscribe(
            params => {        
                this.associated_headers=JSON.parse(params['associated_headers']);
                this.headers=Object.keys(this.associated_headers)
                this.uuid=params['uuid']
                console.log(this.uuid)
            
            }
        );
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
    get_files(){
        
    }
    ngOnInit(): void {
        this.form = this.formBuilder.group({file: ['']});
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
                    this.book = XLSX.read(bstr, { type: "binary" });
                    var first_sheet_name = this.book.SheetNames[0];  
                    this.worksheet = this.book.Sheets[first_sheet_name]; 
                    this.csv = XLSX.utils.sheet_to_csv(this.worksheet);  
                    this.load_csv(this.csv,e) ;
        }  
        fileReader.readAsArrayBuffer(this.fileUploaded);  
    }
    onBrowse(event) {
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
            
            
            this.associated_headers[this.headers[i]]={selected:false,associated_group:""}
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
    }
    
    onSubmit() {
        console.log(this.lines.length)
        if (this.lines.length!==0){
            //console.log(this.form.get('avatar').value)
            //console.log(this.loaded)
            const formData = new FormData();
            formData.append('file', this.form.get('file').value);
            console.log(this.associated_headers)
            console.log(this.fileName)
            console.log(this.book)
            //let user=JSON.parse(localStorage.getItem('currentUser'));
            //let parent_id="studies/981995"
            this.middlewareService.upload(this.fileName,this.associated_headers, this.book).pipe(first()).toPromise().then(data => {console.log(data);})
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
        //console.log(this.selectedOntology)
        console.log(values)
        console.log(key)
          
        this.associated_headers[key]={selected:true, associated_group:values}
    }
    onSelectSpecies(values:string) {
        //console.log(this.selectedOntology)
        console.log(values)

          
        this.species=values
    }
    
    edit_first_group(values:string) {
        //console.log(this.selectedOntology)
        console.log(values)
          
        this.group1_label= values;
        this.select_form.setValue(values);
        //this.select_form.controls["Group1"].patchValue(values)

    }
    edit_second_group(values:string) {
        this.group2_label= values;
        this.select_form.setValue(values);
        //this.select_form.controls["Group2"].patchValue(values)
        //let person = this.peopleForm.get("person").value
    }
    

}


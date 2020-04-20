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
    @Input() data_sample_name:{};
    @Input() uuid:string
    @Input() error:{}
    public error_message:string=""
    
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
    private associated_headers={};
    private lines=[];
    private json_results={}
    uploadResponse = { status: '', message: 0, filePath: '' };
    
    
    // stepper control
    public isLinear = true;
    public firstFormGroup: FormGroup;
    public secondFormGroup: FormGroup;
    public thirdFormGroup: FormGroup;
    
    //group selection
    private selectedColumnKeys: Set<string> = new Set<string>();

    private selectedColumnG1Keys: Set<string> = new Set<string>();
    private selectedColumnG2Keys: Set<string> = new Set<string>();

    selectedheader: string;
    private current_group:string= ""
    
    
    onColumnClick(key: string) {
        
                
        if(this.json_results[this.current_group].has(key)) {
            this.json_results[this.current_group].delete(key);
        }
        else {
            console.log(this.json_results[this.current_group])
            this.json_results[this.current_group].add(key);
        }
//        for (key in Object.keys(this.json_results)){
//            console.log(key)
//            console.log(this.json_results[key])
//        }
    }

    columnBlueIsSelected(key: string) {

        return this.selectedColumnG1Keys.has(key);
    }
    columnGreenIsSelected(key: string) {

        return this.selectedColumnG2Keys.has(key);
    }

    getSelectedColumns(){
        return this.json_results[this.current_group];
    }
    
    
    constructor(private route: ActivatedRoute, private router: Router,  public dialog: MatDialog, public alertService: AlertService, private middlewareService: MiddlewareService,private formBuilder: FormBuilder){
     this.route.queryParams.subscribe(
            params => {    
                //console.log(params)  
                  
                console.log(params['data_sample_name'])
                var sample_names=JSON.parse(params['data_sample_name']);
                var err=JSON.parse(params['error']);
                var sheet_error=err['sheet_error']            
                this.headers=sample_names['header'];
                this.error_message=sample_names['error']                
                this.uuid=params['uuid']
                if (this.error_message === "No Normalized column found"){
                    console.log(this.error_message)
                    this.alertService.info(this.error_message)
                } 
                for (var i = 0; i < this.headers.length; i++){
            
            
                    this.associated_headers[this.headers[i]]={selected:false,associated_group:""}

                }
            }
        );
       }
    get_headers(){
        return this.headers
    }
    
    get_headers_select(){
        return this.headers_select;
    }

    ngOnInit(): void {
        this.form = this.formBuilder.group({file: ['']});
        
        this.firstFormGroup = this.formBuilder.group({
            firstGroupCtrl: ['', Validators.required],
            secondGroupCtrl: ['', Validators.required]
        });
        this.secondFormGroup = this.formBuilder.group({
            GroupradioCtrl: ['', Validators.required]
                 
            });
        this.thirdFormGroup = this.formBuilder.group({
            thirdCtrl: ['', Validators.required]
        });

        
    }
    onChange(event: Event) {
        console.log(event['value']);
        console.log(event['source']['_checked']);
        this.current_group=event['value']
//        let mrButton: MatRadioButton = mrChange.source;
//        console.log(mrButton.name);
//        console.log(mrButton.checked);
//        console.log(mrButton.inputId);
    } 
    onChooseGroup(event: Event){
        this.group1_label = this.firstFormGroup.get("firstGroupCtrl").value
        this.json_results[this.group1_label]=this.selectedColumnG1Keys
        this.group2_label = this.firstFormGroup.get("secondGroupCtrl").value
        this.json_results[this.group2_label]=this.selectedColumnG2Keys
        this.current_group=this.group1_label;
       
        
    } 
    onValidateGroup(event: Event){
        
        console.log(this.json_results)
       
        
    }  
    
    onSelect(select_value:string, key:string) {
        //console.log(this.selectedOntology)
        console.log(select_value)
        console.log(key)
        if (select_value==="undefined"){
            this.associated_headers[key]={selected:false, associated_group:""}
        }
        else{
            this.associated_headers[key]={selected:true, associated_group:select_value}
        } 
        console.log(this.associated_headers)
    }
    
    onSelectSpecies(values:string) {
        //console.log(this.selectedOntology)
        console.log(values)
        this.species=values
    }
    
    
    //last part of stepper
    onSubmit() {
        console.log("Nothing to do yet")
        this.alertService.error("you need to select a file")
    }
    
//    edit_first_group(input_value:string) {
//        //console.log(this.selectedOntology)
//        console.log(input_value)
//          
//        if(input_value === ""){
//            input_value="group1"         
//        }
//        //this.select_form.setValue(input_value);
//        //this.select_form.reset(input_value);
//        this.group1_label= input_value;
//        
//        //this.select_form.controls["Group1"].patchValue(values)
//
//    }
//    edit_second_group(input_value:string) {
//        console.log(input_value)
//        if(input_value === ""){
//            input_value="group2"         
//        }
//        //this.select_form.reset(input_value);
//        //this.select_form.setValue(input_value);
//            this.group2_label= input_value;
//        
//        //this.select_form.controls["Group2"].patchValue(values)
//        //let person = this.peopleForm.get("person").value
//    }
    

}


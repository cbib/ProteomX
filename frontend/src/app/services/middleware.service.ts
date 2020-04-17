import { Injectable } from '@angular/core';
import { HttpClient, HttpEvent, HttpErrorResponse, HttpEventType } from  '@angular/common/http';
import { map } from  'rxjs/operators';
import { throwError, Observable } from 'rxjs';
import {Constants} from "../constants";

@Injectable({
  providedIn: 'root'
})
export class MiddlewareService {
private APIUrl:string;
    constructor(private httpClient: HttpClient) {
    this.APIUrl = Constants.APIConfig.APIUrl;
      }
    private extractData(res: Response) {
        let body = res;
        return body || { };
    }
    public upload(filename:string,associated_headers, book):Observable<any>{
        console.log(associated_headers)
        let obj2send={
            'associated_headers':associated_headers,
            'filename':filename,
            'book':book
            
        };
        return this.httpClient.post(`${this.APIUrl+"upload"}`, obj2send).pipe(map(this.extractData));
    }   
}

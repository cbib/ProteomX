import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
//import { DownloadComponent } from './download/download.component';
import { HomeComponent } from './home/home.component';
//import { DragDropModule} from '@angular/cdk/drag-drop';
//import { DataTablesModule } from 'angular-datatables';

    @NgModule({
  declarations: [
    AppComponent,
    //DownloadComponent,
    HomeComponent
  ],
  imports: [
    BrowserModule,
    AppRoutingModule
    //DataTablesModule,
    //DragDropModule
  ],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }

import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import { AppRoutingModule } from './app-routing.module';
import { AppComponent } from './app.component';
import { HttpClientModule, HTTP_INTERCEPTORS } from '@angular/common/http';
import { DownloadComponent } from './download/download.component';
import { HomeComponent } from './home/home.component';
import { DragDropModule} from '@angular/cdk/drag-drop';
import { DataTablesModule } from 'angular-datatables';
import { DelimitorDialogComponent } from './dialog/delimitor-dialog.component';
import { MatDialogModule } from '@angular/material/dialog';
import { JwtInterceptor, ErrorInterceptor } from './helpers';
import { platformBrowserDynamic} from '@angular/platform-browser-dynamic';
import { BrowserAnimationsModule} from '@angular/platform-browser/animations';
import { MiddlewareService} from './services/middleware.service';
import { AlertService} from './services/alert.service';
import { ReactiveFormsModule,FormsModule }    from '@angular/forms';
import { MetadataDescriptionComponent } from './analysis/metadata-description.component';
import {MatButtonModule} from '@angular/material/button';
import {MatCardModule} from '@angular/material/card';
import { HistoryComponent } from './users/history.component';
import { AlertModule } from './modules/alert.module';
import { ExplorationComponent } from './exploration/exploration.component';
import { QualityCheckComponent } from './quality-check/quality-check.component';

    @NgModule({
  declarations: [
    AppComponent,
    DownloadComponent,
    HomeComponent,
    DelimitorDialogComponent,
    MetadataDescriptionComponent,
    HistoryComponent,
    ExplorationComponent,
    QualityCheckComponent,
    
  ],
  imports: [
    BrowserModule,
    AppRoutingModule,
    DataTablesModule,
    DragDropModule,
    MatDialogModule,
    BrowserAnimationsModule,
    ReactiveFormsModule,
    FormsModule,
    HttpClientModule,
    MatButtonModule,
    MatCardModule,
    AlertModule
    
  ],
  entryComponents:[DelimitorDialogComponent],

  providers: [MiddlewareService, AlertService, { provide: HTTP_INTERCEPTORS, useClass: JwtInterceptor, multi: true },
              { provide: HTTP_INTERCEPTORS, useClass: ErrorInterceptor, multi: true },],
  
  bootstrap: [AppComponent]
})
export class AppModule { }

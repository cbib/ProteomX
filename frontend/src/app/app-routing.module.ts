import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from './home/home.component';
//import { DownloadComponent } from './download/download.component';

const routes: Routes = [
{ path: 'home',component: HomeComponent}
//{ path: 'download',component: DownloadComponent}
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {
    onSameUrlNavigation: 'reload'
  })],
  exports: [RouterModule]
})
export class AppRoutingModule { }                                   

import { NgModule } from '@angular/core';
import { Routes, RouterModule } from '@angular/router';
import { HomeComponent } from './home/home.component';
import { DownloadComponent } from './download/download.component';
import { MetadataDescriptionComponent } from './analysis/metadata-description.component';
import { HistoryComponent } from './users/history.component'
import { ExplorationComponent } from './exploration/exploration.component';
import { QualityCheckComponent } from './quality-check/quality-check.component';


const routes: Routes = [
{ path: 'home',component: HomeComponent},
{ path: 'download',component: DownloadComponent},
{ path: 'metadata',component: MetadataDescriptionComponent},
{ path: 'history',component: HistoryComponent},
{ path: 'exploration',component: ExplorationComponent},
{ path: 'quality-check',component: QualityCheckComponent},
{ path: '',redirectTo: '/home',pathMatch: 'full'},
{ path: '**',redirectTo: '/home',pathMatch: 'full'}
];

@NgModule({
  imports: [RouterModule.forRoot(routes, {
    onSameUrlNavigation: 'reload'
  })],
  exports: [RouterModule]
})
export class AppRoutingModule { }                                   

import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { DelimitorDialogComponent } from './delimitor-dialog.component';

describe('DelimitorDialogComponent', () => {
  let component: DelimitorDialogComponent;
  let fixture: ComponentFixture<DelimitorDialogComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ DelimitorDialogComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(DelimitorDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

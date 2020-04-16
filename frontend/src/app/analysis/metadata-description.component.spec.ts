import { async, ComponentFixture, TestBed } from '@angular/core/testing';

import { MetadataDescriptionComponent } from './metadata-description.component';

describe('MetadataDescriptionComponent', () => {
  let component: MetadataDescriptionComponent;
  let fixture: ComponentFixture<MetadataDescriptionComponent>;

  beforeEach(async(() => {
    TestBed.configureTestingModule({
      declarations: [ MetadataDescriptionComponent ]
    })
    .compileComponents();
  }));

  beforeEach(() => {
    fixture = TestBed.createComponent(MetadataDescriptionComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

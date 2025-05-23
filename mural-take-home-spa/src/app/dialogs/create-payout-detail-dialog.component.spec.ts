import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CreatePayoutDetailDialogComponent } from './create-payout-detail-dialog.component';

describe('CreatePayoutDetailDialogComponent', () => {
  let component: CreatePayoutDetailDialogComponent;
  let fixture: ComponentFixture<CreatePayoutDetailDialogComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CreatePayoutDetailDialogComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CreatePayoutDetailDialogComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});

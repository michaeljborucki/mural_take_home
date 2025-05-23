import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatSelectModule } from '@angular/material/select';
import { MatOptionModule } from '@angular/material/core';
import { MatButtonModule } from '@angular/material/button';
import { OrganizationCreationRequest } from '../models/organization-creation-request.model';
import { OrganizationService } from '../services/organization.service';

@Component({
  standalone: true,
  selector: 'app-create-organization-dialog',
  templateUrl: './create-organization-dialog.component.html',
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatSelectModule,
    MatOptionModule,
    MatButtonModule
  ]
})
export class CreateOrganizationDialogComponent {
  formData: OrganizationCreationRequest = {
    type: 'individual',
    email: ''
  };
  isSubmitting = false;

  constructor(
    public dialogRef: MatDialogRef<CreateOrganizationDialogComponent>,
    private organizationService: OrganizationService
  ) {}

  onSubmit(): void {
    if (this.isSubmitting) return;
    this.isSubmitting = true;

    this.organizationService.createOrganization(this.formData).subscribe({
      next: (createdOrg) => {
        this.dialogRef.close(createdOrg); // return created org to parent
      },
      error: (err) => {
        console.error('Failed to create organization:', err);
        this.isSubmitting = false;
        // optionally show error to user
      }
    });
  }

  onCancel(): void {
    this.dialogRef.close(null);
  }
}

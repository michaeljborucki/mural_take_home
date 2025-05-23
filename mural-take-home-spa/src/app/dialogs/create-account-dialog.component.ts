import { Component } from '@angular/core';
import { MatDialogRef } from '@angular/material/dialog';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';

@Component({
  standalone: true,
  selector: 'app-create-account-dialog',
  templateUrl: './create-account-dialog.component.html',
  imports: [CommonModule, FormsModule, MatFormFieldModule, MatInputModule, MatButtonModule]
})
export class CreateAccountDialogComponent {
  formData = {
    name: '',
    description: ''
  };
  isSubmitting = false;

  constructor(public dialogRef: MatDialogRef<CreateAccountDialogComponent>) {}

  onSubmit(): void {
    if (this.isSubmitting) return;
    this.isSubmitting = true;
    this.dialogRef.close(this.formData);
  }

  onCancel(): void {
    this.dialogRef.close(null);
  }
}

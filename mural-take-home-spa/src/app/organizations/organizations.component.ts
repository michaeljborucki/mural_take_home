import { Component } from '@angular/core';
import { OrganizationService } from '../services/organization.service';
import { Organization } from '../models/organization.model';
import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatToolbarModule } from '@angular/material/toolbar';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { MatIconModule } from '@angular/material/icon';
import { FormsModule } from '@angular/forms';
import { MatOptionModule } from '@angular/material/core';
import { MatFormFieldModule } from '@angular/material/form-field';
import { OrganizationCreationRequest } from '../models/organization-creation-request.model';
import { MatDialog } from '@angular/material/dialog';
import { CreateOrganizationDialogComponent } from '../dialogs/create-organization-dialog.component';



@Component({
  selector: 'app-organizations',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatCardModule,
    MatToolbarModule,
    RouterLink,
    MatIconModule,
    FormsModule,
    MatFormFieldModule,
    MatOptionModule
  ],
  templateUrl: './organizations.component.html',
  styleUrls: ['./organizations.component.css'],
  providers: [OrganizationService]
})
export class OrganizationsComponent {
  displayedColumns: string[] = ['name', 'type', 'kycStatus', 'tosStatus', 'createdAt'];
  dataSource: Organization[] = [];
  showCreateForm = false;
  newOrganization: OrganizationCreationRequest = {
    type: 'individual',
    email: ''
  };

  constructor(private organizationService: OrganizationService, private dialog: MatDialog) {}

  ngOnInit(): void {
    this.fetchOrganizations()
  }

  fetchOrganizations(): void{
    this.organizationService.getOrganizationListData().subscribe({
      next: (data) => {
        console.log('Organization List:', data);
  
        // ✅ Extract orgIds and save to localStorage
        const orgSummaries = data.map((org: any) => ({
          id: org.id,
          name: org.name ?? `${org.firstName} ${org.lastName}`,
          active:
            org.tosStatus === 'ACCEPTED' &&
            org.kycStatus.type === 'approved'
        }));
        const payload = {
          data: orgSummaries,
          timestamp: Date.now() // milliseconds since epoch
        };
        localStorage.setItem('orgIds', JSON.stringify(payload));
        this.dataSource = data;
      },
      error: (err) => console.error('Error:', err)
    });
  }

  openCreateDialog(): void {
    const dialogRef = this.dialog.open(CreateOrganizationDialogComponent);
  
    dialogRef.afterClosed().subscribe((result) => {
      if (result) {
        this.organizationService.createOrganization(result).subscribe({
          next: (createdOrg) => {
            this.fetchOrganizations(); // ✅ fetch latest list
          },
          error: (err) => console.error('Failed to create organization:', err)
        });
      }
    });
  }
  
}

import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Organization } from '../models/organization.model';
import { OrganizationCreationRequest } from '../models/organization-creation-request.model';

@Injectable({
  providedIn: 'root'
})
export class OrganizationService {

  private organizationApiURL = '/api/organizations';

  constructor(private http: HttpClient) {}

  // Returns a list of organizations
  getOrganizationListData(): Observable<Organization[]> {
    return this.http.get<Organization[]>(this.organizationApiURL);
  }

  // Returns details of a single organization
  getOrganizationData(orgId: string): Observable<Organization> {
    return this.http.get<Organization>(`${this.organizationApiURL}/${orgId}`);
  }

  createOrganization(organizationRequest: OrganizationCreationRequest){
    return this.http.post<Organization>(this.organizationApiURL, organizationRequest);
  }
}

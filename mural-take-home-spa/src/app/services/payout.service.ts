import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { Payout } from '../models/payout.model';
import { PayoutRequest } from '../models/payout-request.model';

@Injectable({
  providedIn: 'root'
})
export class PayoutService {

  private payoutEndpoint = '/api/payouts';

  constructor(private http: HttpClient) {}

  // Returns a list of payouts per organization
  getPayoutData(org_id: string, acc_id: string, body: any): Observable<Payout[]> {
    const url = `${this.payoutEndpoint}/${org_id}/${acc_id}`;
    return this.http.post<Payout[]>(url, body);
  }

  executePayoutRequest(org_id: string, acc_id: string, payout_id: string): Observable<Payout> {
    const url = `${this.payoutEndpoint}/${org_id}/${acc_id}/${payout_id}`;
    return this.http.post<Payout>(url, {});
  }
  createPayout(org_id:string, request_body: PayoutRequest): any{
    const url = `${this.payoutEndpoint}/create/${org_id}`;
    return this.http.post<Payout>(url, request_body);
  }
  // // Returns details of a single organization
  // getOrganizationData(orgId: string): Observable<Organization> {
  //   return this.http.get<Organization>(`${this.organizationApiURL}/${orgId}`);
  // }

  // createOrganization(organizationRequest: OrganizationCreationRequest){
  //   return this.http.post<Organization>(this.organizationApiURL, organizationRequest);
  // }
}

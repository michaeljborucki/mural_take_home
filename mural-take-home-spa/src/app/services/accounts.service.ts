import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http'
import { Observable } from 'rxjs'
import { Account } from '../models/account.model';

@Injectable({
  providedIn: 'root'
})
export class AccountsService {
  private accountEndpoint = '/api/accounts';

  constructor(private http: HttpClient) {}

  // Returns a list of accounts for an organization
  getAccountListData(orgId: string): Observable<Account[]> {
    return this.http.get<Account[]>(`${this.accountEndpoint}/${orgId}`);
  }

  // Returns details of a single account
  getAccountData(orgId: string, accountId: string): Observable<Account> {
    return this.http.get<Account>(`${this.accountEndpoint}/${orgId}/${accountId}`);
  }

  createAccount(orgId: string, request: any): Observable<Account> {
    return this.http.post<Account>(`${this.accountEndpoint}/${orgId}`, request);
  }
}

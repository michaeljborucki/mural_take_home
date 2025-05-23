// ipinfo.service.ts
import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class IpinfoService {
bannedCountries: string[] = ["RUS", "NK", "US"]
  constructor(private http: HttpClient) {}

  getIpInfo(): Observable<any> {
    return this.http.get('https://ipinfo.io/json?token=09350aad6ca0e5');
  }

  isCountryRestricted(country: string): Boolean{
    return this.bannedCountries.includes(country)
  }
}

import { Component } from '@angular/core';
import { RouterModule, RouterOutlet } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatCardModule } from '@angular/material/card';
import { MatToolbarModule } from '@angular/material/toolbar';
import { IpinfoService } from './services/ipinfo.service';
import { CommonModule } from '@angular/common';
import { MatIconModule } from '@angular/material/icon';

@Component({
  selector: 'app-root',
  imports: [
    RouterModule,
    RouterOutlet,
    MatTableModule,
    MatCardModule,
    MatToolbarModule,
    CommonModule,
    MatIconModule
  ],
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
})
export class AppComponent {
  title = 'Mural SPA';
  userLocation: string = '';
  userWarning: string = '';
  constructor(
    private ipInfoService: IpinfoService
  ) {}

  ngOnInit(): void {
    this.ipInfoService.getIpInfo().subscribe({
      next: (data) => {
        this.userLocation = `${data.city}, ${data.region}, ${data.country}`;
        if(this.ipInfoService.isCountryRestricted(data.country)){
          this.userWarning = 'WARNING: User in Restricted Country';
        }
      },
      error: (err) => {
        console.error('Failed to fetch IP info:', err);
        this.userLocation = 'Location unavailable';
      }
    });
  }

}

import { OrganizationService } from "./app/services/organization.service";

export function getOrgIdsWithCaching(orgService: OrganizationService): Promise<any[]> {
    const cached = localStorage.getItem('orgIds');
    const now = Date.now();
    const twoMinutes = 2 * 60 * 1000;
  
    if (cached) {
      try {
        const parsed = JSON.parse(cached);
        if (now - parsed.timestamp <= twoMinutes) {
          // ✅ Cache is valid
          return Promise.resolve(parsed.data);
        }
      } catch (err) {
        console.warn('Invalid cache format, ignoring cache');
      }
    }
  
    // Cache is expired or invalid — fetch from API
    return new Promise((resolve, reject) => {
      orgService.getOrganizationListData().subscribe({
        next: (data) => {
          const orgSummaries = data.map((org: any) => ({
            id: org.id,
            name: org.name ?? `${org.firstName} ${org.lastName}`,
            active:
              org.tosStatus === 'ACCEPTED' &&
              org.kycStatus.type === 'approved'
          }));
          
          const payload = {
            data: orgSummaries,
            timestamp: now
          };
          
          localStorage.setItem('orgIds', JSON.stringify(payload));
          resolve(orgSummaries); // return array of IDs only
        },
        error: (err) => {
          console.error('Failed to fetch orgs:', err);
          reject(err);
        }
      });
    });
  }
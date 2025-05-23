export interface Account {
    id: string;
    name: string;
    status: string;
    isApiEnabled: boolean;
    createdAt: string;
    updatedAt: string;
    accountDetails: {
      balances: {
        tokenAmount: number;
        tokenSymbol: string;
      }[];
      depositAccount: {
        accountId: string;
        bankAccountNumber: string;
        bankAddress: string;
        bankBeneficiaryAddress: string;
        bankBeneficiaryName: string;
        bankName: string;
        bankRoutingNumber: string;
        currency: string;
        id: string;
        paymentRails: string[];
        status: string;
      };
      walletDetails: {
        blockchain: string;
        walletAddress: string;
      };
    };
  }
  
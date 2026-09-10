export type LabData = {
  id: string;
  name: string;
  location: string;
  distance: string;
  nabl: boolean;
  bis: boolean;
  turnaroundTime: string;
  feeRange: string;
};

export const mockLabs: LabData[] = [
  {
    id: "l1",
    name: "National Test House (NTH)",
    location: "Mumbai, Maharashtra",
    distance: "12 km away",
    nabl: true,
    bis: true,
    turnaroundTime: "7-10 Days",
    feeRange: "₹15,000 - ₹25,000",
  },
  {
    id: "l2",
    name: "TUV SUD South Asia Pvt. Ltd.",
    location: "Pune, Maharashtra",
    distance: "145 km away",
    nabl: true,
    bis: true,
    turnaroundTime: "5-7 Days",
    feeRange: "₹20,000 - ₹35,000",
  },
  {
    id: "l3",
    name: "Electronics Regional Test Laboratory (ERTL)",
    location: "New Delhi, Delhi",
    distance: "1,100 km away",
    nabl: true,
    bis: true,
    turnaroundTime: "10-15 Days",
    feeRange: "₹12,000 - ₹18,000",
  },
  {
    id: "l4",
    name: "Spectro Analytical Labs",
    location: "Noida, UP",
    distance: "1,120 km away",
    nabl: true,
    bis: false,
    turnaroundTime: "4-6 Days",
    feeRange: "₹10,000 - ₹15,000",
  },
  {
    id: "l5",
    name: "Intertek India Private Limited",
    location: "Bengaluru, Karnataka",
    distance: "840 km away",
    nabl: true,
    bis: true,
    turnaroundTime: "6-8 Days",
    feeRange: "₹22,000 - ₹40,000",
  }
];

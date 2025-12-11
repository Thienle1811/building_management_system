import axiosClient from './axiosClient';

const billingApi = {
  // Lấy danh sách hóa đơn của căn hộ mình
  getMyInvoices: () => {
    return axiosClient.get('billing/my-invoices/');
  },
  
  // Gửi ảnh chuyển khoản (Upload Proof)
  uploadPaymentProof: (invoiceId: number, formData: any) => {
    return axiosClient.post(`billing/invoices/${invoiceId}/upload_proof/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  }
};

export default billingApi;
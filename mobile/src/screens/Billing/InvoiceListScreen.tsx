import React, { useEffect, useState } from 'react';
import { View, Text, FlatList, StyleSheet, ActivityIndicator, RefreshControl, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import billingApi from '../../api/billingApi';

const InvoiceListScreen = ({ navigation }: any) => {
  const [invoices, setInvoices] = useState([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const fetchInvoices = async () => {
    try {
      const res = await billingApi.getMyInvoices();
      setInvoices(res.data);
    } catch (error) {
      console.log('Lỗi lấy hóa đơn:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, []);

  const renderItem = ({ item }: any) => {
    const isPaid = item.status === 'PAID';
    return (
      <TouchableOpacity style={styles.card}>
        <View style={styles.cardHeader}>
          <View style={{flexDirection:'row', alignItems:'center'}}>
            <Ionicons 
              name={item.title.includes('Điện') ? 'flash' : item.title.includes('Nước') ? 'water' : 'receipt'} 
              size={20} color="#666" 
            />
            <Text style={styles.title}>{item.title}</Text>
          </View>
          <Text style={[styles.status, { color: isPaid ? 'green' : 'red', backgroundColor: isPaid ? '#d4edda' : '#f8d7da' }]}>
            {item.status_display}
          </Text>
        </View>

        <View style={styles.cardBody}>
          <Text style={styles.amount}>{parseInt(item.total_amount).toLocaleString('vi-VN')} đ</Text>
          <Text style={styles.date}>Kỳ hạn: {item.period}</Text>
        </View>

        {!isPaid && (
          <View style={styles.cardFooter}>
            <Text style={styles.helperText}>Vui lòng chuyển khoản cho BQL</Text>
            <Ionicons name="chevron-forward" size={18} color="#ccc" />
          </View>
        )}
      </TouchableOpacity>
    );
  };

  return (
    <View style={styles.container}>
      {loading ? (
        <ActivityIndicator size="large" color="#0d6efd" style={{marginTop: 20}} />
      ) : (
        <FlatList
          data={invoices}
          keyExtractor={(item: any) => item.id.toString()}
          renderItem={renderItem}
          contentContainerStyle={{ padding: 15 }}
          refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); fetchInvoices(); }} />}
          ListEmptyComponent={<Text style={styles.empty}>Bạn không có hóa đơn nào.</Text>}
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8f9fa' },
  card: { backgroundColor: '#fff', borderRadius: 10, padding: 15, marginBottom: 12, elevation: 2 },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 10 },
  title: { fontWeight: 'bold', fontSize: 16, marginLeft: 8, color: '#333' },
  status: { fontSize: 12, fontWeight: 'bold', paddingHorizontal: 8, paddingVertical: 2, borderRadius: 5, overflow: 'hidden' },
  cardBody: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-end' },
  amount: { fontSize: 20, fontWeight: 'bold', color: '#0d6efd' },
  date: { color: '#6c757d' },
  cardFooter: { marginTop: 10, paddingTop: 10, borderTopWidth: 1, borderTopColor: '#eee', flexDirection: 'row', justifyContent: 'space-between' },
  helperText: { color: '#adb5bd', fontSize: 12, fontStyle: 'italic' },
  empty: { textAlign: 'center', marginTop: 50, color: '#999' }
});

export default InvoiceListScreen;
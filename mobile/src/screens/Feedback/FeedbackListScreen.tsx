import React, { useEffect, useState } from 'react';
import { 
  View, Text, FlatList, StyleSheet, TouchableOpacity, 
  RefreshControl, ActivityIndicator 
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context'; // <--- MỚI THÊM
import feedbackApi, { Feedback } from '../../api/feedbackApi';
import { useNavigation } from '@react-navigation/native';

const FeedbackListScreen = () => {
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  const [loading, setLoading] = useState(true);
  const navigation = useNavigation();

  // Hàm gọi API lấy dữ liệu
  const loadData = async () => {
    try {
      setLoading(true);
      const response: any = await feedbackApi.getMyFeedbacks();
      setFeedbacks(response.data);
    } catch (error) {
      console.log('Lỗi lấy danh sách:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const renderStatusBadge = (status: string, label: string) => {
    let color = '#6c757d';
    if (status === 'PENDING') color = '#ffc107';
    else if (status === 'PROCESSING') color = '#0d6efd';
    else if (status === 'DONE') color = '#198754';
    else if (status === 'CANCELLED') color = '#dc3545';

    return (
      <View style={[styles.badge, { backgroundColor: color }]}>
        <Text style={styles.badgeText}>{label}</Text>
      </View>
    );
  };

  const renderItem = ({ item }: { item: Feedback }) => (
    <TouchableOpacity style={styles.card} activeOpacity={0.7}>
      <View style={styles.cardHeader}>
        <Text style={styles.code}>#{item.code}</Text>
        {renderStatusBadge(item.status, item.status_display)}
      </View>
      
      <Text style={styles.title} numberOfLines={2}>{item.title}</Text>
      <Text style={styles.category}>{item.category_name}</Text>
      
      <View style={styles.cardFooter}>
        <Text style={styles.date}>
          {new Date(item.created_at).toLocaleDateString('vi-VN')} {new Date(item.created_at).toLocaleTimeString('vi-VN', {hour: '2-digit', minute:'2-digit'})}
        </Text>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      {/* --- SỬA ĐOẠN NÀY: Dùng SafeAreaView bọc Header --- */}
      <View style={{ backgroundColor: '#fff' }}>
        <SafeAreaView edges={['top']}>
          <View style={styles.headerContainer}>
            <Text style={styles.headerTitle}>Lịch sử phản ánh</Text>
            <TouchableOpacity 
                style={styles.addButton}
                onPress={() => navigation.navigate('CreateFeedback' as never)}
            >
                <Text style={styles.addButtonText}>+ Gửi yêu cầu</Text>
            </TouchableOpacity>
          </View>
        </SafeAreaView>
      </View>
      {/* ------------------------------------------------ */}

      {loading && feedbacks.length === 0 ? (
        <ActivityIndicator size="large" color="#0d6efd" style={{ marginTop: 20 }} />
      ) : (
        <FlatList
          data={feedbacks}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderItem}
          refreshControl={<RefreshControl refreshing={loading} onRefresh={loadData} />}
          contentContainerStyle={styles.listContent}
          ListEmptyComponent={
            <Text style={styles.emptyText}>Bạn chưa gửi phản hồi nào.</Text>
          }
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f5f7fa' },
  headerContainer: { 
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', 
    padding: 15, 
    // backgroundColor: '#fff', // Bỏ background ở đây vì đã đặt ở View cha
    elevation: 2 
  },
  headerTitle: { fontSize: 18, fontWeight: 'bold', color: '#333' },
  addButton: { backgroundColor: '#0d6efd', paddingHorizontal: 15, paddingVertical: 8, borderRadius: 20 },
  addButtonText: { color: '#fff', fontWeight: 'bold', fontSize: 14 },
  
  listContent: { padding: 15 },
  
  card: { 
    backgroundColor: '#fff', borderRadius: 10, padding: 15, marginBottom: 12, 
    shadowColor: '#000', shadowOpacity: 0.05, shadowRadius: 5, elevation: 2 
  },
  cardHeader: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 8 },
  code: { fontWeight: 'bold', color: '#999', fontSize: 12 },
  badge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 4 },
  badgeText: { color: '#fff', fontSize: 10, fontWeight: 'bold' },
  
  title: { fontSize: 16, fontWeight: 'bold', color: '#333', marginBottom: 4 },
  category: { color: '#0d6efd', fontSize: 13, marginBottom: 8 },
  
  cardFooter: { borderTopWidth: 1, borderTopColor: '#f1f1f1', paddingTop: 8, alignItems: 'flex-end' },
  date: { color: '#adb5bd', fontSize: 12 },
  emptyText: { textAlign: 'center', marginTop: 50, color: '#6c757d' }
});

export default FeedbackListScreen;
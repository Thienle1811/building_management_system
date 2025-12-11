import React, { useState, useCallback } from 'react';
import { 
  View, Text, FlatList, StyleSheet, TouchableOpacity, 
  RefreshControl, ActivityIndicator 
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useFocusEffect } from '@react-navigation/native'; // <--- (1) Import quan trọng
import * as Notifications from 'expo-notifications';
import notificationApi, { Notification } from '../../api/notificationApi';

const NotificationScreen = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  // Hàm gọi API lấy dữ liệu
  const loadData = async () => {
    try {
      // Mẹo nhỏ: Nếu đang loading thì thôi, tránh spam request
      // setLoading(true); <--- Có thể bỏ dòng này nếu muốn trải nghiệm mượt hơn (silent refresh)
      
      const response: any = await notificationApi.getAll();
      setNotifications(response.data);
    } catch (error) {
      console.log('Lỗi lấy thông báo:', error);
    } finally {
      setLoading(false);
    }
  };

  // (2) Dùng useFocusEffect thay cho useEffect
  // Tự động chạy mỗi khi người dùng chuyển sang tab này hoặc mở app vào màn hình này
  useFocusEffect(
    useCallback(() => {
      console.log("👀 Màn hình Thông báo đang được hiển thị -> Load data...");
      setLoading(true); // Hiện xoay xoay cho người dùng biết đang cập nhật
      loadData();

      // --- LẮNG NGHE SỰ KIỆN PUSH KHI ĐANG Ở MÀN HÌNH NÀY ---
      // Khi có thông báo mới bay tới, tự động load lại luôn
      const subscription = Notifications.addNotificationReceivedListener(notification => {
        console.log("🔔 Có tin mới nhận được, tự refresh...");
        loadData();
      });

      return () => {
        // Hủy lắng nghe khi rời khỏi màn hình này
        subscription.remove();
      };
    }, [])
  );

  // Xử lý khi bấm vào thông báo
  const handlePressItem = async (item: Notification) => {
    if (!item.is_read) {
      notificationApi.markRead(item.id);
      // Cập nhật giao diện giả lập (Optimistic update) cho nhanh
      const updatedList = notifications.map(n => 
        n.id === item.id ? { ...n, is_read: true } : n
      );
      setNotifications(updatedList);
    }
  };

  const handleMarkAllRead = async () => {
    await notificationApi.markAllRead();
    loadData();
  };

  const renderItem = ({ item }: { item: Notification }) => (
    <TouchableOpacity 
      style={[styles.card, !item.is_read && styles.unreadCard]} 
      onPress={() => handlePressItem(item)}
      activeOpacity={0.7}
    >
      <View style={styles.row}>
        <View style={[styles.iconBox, item.notification_type === 'SYSTEM' ? styles.bgInfo : styles.bgWarning]}>
          <Ionicons 
            name={item.notification_type === 'SYSTEM' ? 'information-circle' : 'chatbubble-ellipses'} 
            size={24} color="#fff" 
          />
        </View>
        
        <View style={styles.content}>
          <View style={styles.header}>
            <Text style={styles.date}>{item.created_at_display}</Text>
            {!item.is_read && <View style={styles.dot} />}
          </View>
          
          <Text style={[styles.title, !item.is_read && styles.unreadText]}>
            {item.title}
          </Text>
          <Text style={styles.body} numberOfLines={3}>
            {item.body}
          </Text>
        </View>
      </View>
    </TouchableOpacity>
  );

  return (
    <View style={styles.container}>
      <View style={styles.toolbar}>
        <Text style={styles.heading}>Thông báo</Text>
        <TouchableOpacity onPress={handleMarkAllRead}>
          <Text style={styles.markReadText}>Đánh dấu đã đọc</Text>
        </TouchableOpacity>
      </View>

      {/* Hiển thị Loading khi danh sách trống */}
      {loading && notifications.length === 0 ? (
        <ActivityIndicator size="large" color="#0d6efd" style={{ marginTop: 20 }} />
      ) : (
        <FlatList
          data={notifications}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderItem}
          // Vẫn giữ tính năng kéo xuống để refresh thủ công
          refreshControl={<RefreshControl refreshing={loading} onRefresh={loadData} />}
          contentContainerStyle={{ padding: 15 }}
          ListEmptyComponent={
            <Text style={styles.emptyText}>Bạn không có thông báo nào.</Text>
          }
        />
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff' },
  toolbar: { 
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', 
    padding: 15, borderBottomWidth: 1, borderBottomColor: '#f0f0f0' 
  },
  heading: { fontSize: 20, fontWeight: 'bold' },
  markReadText: { color: '#0d6efd', fontWeight: '600' },
  
  card: { 
    padding: 15, borderRadius: 12, marginBottom: 12, backgroundColor: '#f8f9fa',
    borderWidth: 1, borderColor: '#eee'
  },
  unreadCard: { 
    backgroundColor: '#e7f1ff', borderColor: '#b6d4fe' 
  },
  row: { flexDirection: 'row' },
  iconBox: { 
    width: 45, height: 45, borderRadius: 25, 
    justifyContent: 'center', alignItems: 'center', marginRight: 15 
  },
  bgInfo: { backgroundColor: '#17a2b8' },
  bgWarning: { backgroundColor: '#ffc107' },
  
  content: { flex: 1 },
  header: { flexDirection: 'row', justifyContent: 'space-between', marginBottom: 5 },
  date: { fontSize: 12, color: '#888' },
  dot: { width: 8, height: 8, borderRadius: 4, backgroundColor: '#0d6efd' },
  
  title: { fontSize: 16, fontWeight: '600', marginBottom: 4, color: '#333' },
  unreadText: { fontWeight: 'bold', color: '#000' },
  body: { fontSize: 14, color: '#555', lineHeight: 20 },
  
  emptyText: { textAlign: 'center', marginTop: 50, color: '#888' }
});

export default NotificationScreen;
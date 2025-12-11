// src/screens/Feedback/CreateFeedbackScreen.tsx

import React, { useState, useEffect } from 'react';
import {
  View, Text, TextInput, StyleSheet, TouchableOpacity, ScrollView,
  Alert, Image, ActivityIndicator, Modal, FlatList
} from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { useNavigation } from '@react-navigation/native';
import feedbackApi, { FeedbackCategory } from '../../api/feedbackApi';

const CreateFeedbackScreen = () => {
  const navigation = useNavigation();
  
  // State quản lý dữ liệu form
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [categoryId, setCategoryId] = useState<number | null>(null);
  const [images, setImages] = useState<any[]>([]);
  
  // State dữ liệu danh mục & loading
  const [categories, setCategories] = useState<FeedbackCategory[]>([]);
  const [loadingCategory, setLoadingCategory] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  
  // State cho Modal chọn danh mục
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedCategoryName, setSelectedCategoryName] = useState('Chọn danh mục...');

  // 1. Lấy danh sách danh mục khi vào màn hình
  useEffect(() => {
    const fetchCategories = async () => {
      try {
        setLoadingCategory(true);
        const response: any = await feedbackApi.getCategories();
        setCategories(response.data);
      } catch (error) {
        Alert.alert('Lỗi', 'Không thể tải danh mục phản hồi');
      } finally {
        setLoadingCategory(false);
      }
    };
    fetchCategories();
  }, []);

  // 2. Hàm chọn ảnh từ thư viện
  const pickImage = async () => {
    // Xin quyền truy cập thư viện
    const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (status !== 'granted') {
      Alert.alert('Quyền truy cập', 'Cần cấp quyền truy cập ảnh để tải lên.');
      return;
    }

    let result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      allowsEditing: false, // Chọn nhiều ảnh thì không edit
      quality: 0.8,
      allowsMultipleSelection: true, // Cho phép chọn nhiều ảnh (Expo SDK 46+)
      selectionLimit: 3, // Tối đa 3 ảnh
    });

    if (!result.canceled) {
      // Thêm ảnh mới vào danh sách hiện tại
      setImages([...images, ...result.assets]);
    }
  };

  // 3. Hàm xóa ảnh đã chọn
  const removeImage = (index: number) => {
    const newImages = [...images];
    newImages.splice(index, 1);
    setImages(newImages);
  };

  // 4. Hàm Gửi Phản hồi
  const handleSubmit = async () => {
    if (!title.trim()) {
      Alert.alert('Thiếu thông tin', 'Vui lòng nhập tiêu đề');
      return;
    }
    if (!categoryId) {
      Alert.alert('Thiếu thông tin', 'Vui lòng chọn danh mục');
      return;
    }

    try {
      setSubmitting(true);
      await feedbackApi.createFeedback(title, description, categoryId, images);
      
      Alert.alert('Thành công', 'Gửi phản hồi thành công!', [
        { text: 'OK', onPress: () => navigation.goBack() }
      ]);
    } catch (error) {
      console.log('Lỗi gửi phản hồi:', error);
      Alert.alert('Thất bại', 'Có lỗi xảy ra, vui lòng thử lại.');
    } finally {
      setSubmitting(false);
    }
  };

  // --- UI Render ---
  return (
    <ScrollView style={styles.container} contentContainerStyle={{paddingBottom: 30}}>
      
      {/* Chọn Danh mục */}
      <Text style={styles.label}>Danh mục phản hồi <Text style={styles.required}>*</Text></Text>
      <TouchableOpacity 
        style={styles.dropdown} 
        onPress={() => setModalVisible(true)}
      >
        <Text style={{color: categoryId ? '#000' : '#999'}}>{selectedCategoryName}</Text>
        <Text>▼</Text>
      </TouchableOpacity>

      {/* Nhập Tiêu đề */}
      <Text style={styles.label}>Tiêu đề <Text style={styles.required}>*</Text></Text>
      <TextInput
        style={styles.input}
        placeholder="Ví dụ: Bóng đèn hành lang hỏng"
        value={title}
        onChangeText={setTitle}
      />

      {/* Nhập Mô tả */}
      <Text style={styles.label}>Nội dung chi tiết</Text>
      <TextInput
        style={[styles.input, styles.textArea]}
        placeholder="Mô tả chi tiết vấn đề..."
        value={description}
        onChangeText={setDescription}
        multiline
        numberOfLines={4}
        textAlignVertical="top"
      />

      {/* Chọn Ảnh */}
      <Text style={styles.label}>Hình ảnh đính kèm (Tối đa 3)</Text>
      <View style={styles.imageContainer}>
        {images.map((img, index) => (
          <View key={index} style={styles.imageWrapper}>
            <Image source={{ uri: img.uri }} style={styles.thumbnail} />
            <TouchableOpacity 
                style={styles.removeBtn} 
                onPress={() => removeImage(index)}
            >
              <Text style={styles.removeBtnText}>X</Text>
            </TouchableOpacity>
          </View>
        ))}
        
        {images.length < 3 && (
          <TouchableOpacity style={styles.uploadBtn} onPress={pickImage}>
            <Text style={styles.uploadIcon}>+</Text>
            <Text style={styles.uploadText}>Thêm ảnh</Text>
          </TouchableOpacity>
        )}
      </View>

      {/* Nút Gửi */}
      <TouchableOpacity 
        style={[styles.submitBtn, submitting && styles.disabledBtn]} 
        onPress={handleSubmit}
        disabled={submitting}
      >
        {submitting ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.submitBtnText}>GỬI YÊU CẦU</Text>
        )}
      </TouchableOpacity>

      {/* Modal Chọn Danh mục */}
      <Modal visible={modalVisible} transparent animationType="slide">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>Chọn Danh mục</Text>
            {loadingCategory ? (
              <ActivityIndicator size="large" color="#0d6efd" />
            ) : (
              <FlatList
                data={categories}
                keyExtractor={(item) => item.id.toString()}
                renderItem={({ item }) => (
                  <TouchableOpacity 
                    style={styles.modalItem}
                    onPress={() => {
                      setCategoryId(item.id);
                      setSelectedCategoryName(item.name);
                      setModalVisible(false);
                    }}
                  >
                    <Text style={styles.modalItemText}>{item.name}</Text>
                  </TouchableOpacity>
                )}
              />
            )}
            <TouchableOpacity 
                style={styles.closeModalBtn} 
                onPress={() => setModalVisible(false)}
            >
              <Text style={styles.closeModalText}>Đóng</Text>
            </TouchableOpacity>
          </View>
        </View>
      </Modal>

    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', padding: 20 },
  label: { fontWeight: 'bold', marginBottom: 8, color: '#333' },
  required: { color: 'red' },
  
  input: { 
    borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 12, 
    marginBottom: 20, backgroundColor: '#f9f9f9', fontSize: 16 
  },
  textArea: { height: 100 },
  
  dropdown: {
    borderWidth: 1, borderColor: '#ddd', borderRadius: 8, padding: 12,
    marginBottom: 20, backgroundColor: '#f9f9f9',
    flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center'
  },

  // Image Styles
  imageContainer: { flexDirection: 'row', flexWrap: 'wrap', marginBottom: 30 },
  imageWrapper: { position: 'relative', marginRight: 10, marginBottom: 10 },
  thumbnail: { width: 80, height: 80, borderRadius: 8 },
  removeBtn: { 
    position: 'absolute', top: -5, right: -5, backgroundColor: 'red', 
    width: 20, height: 20, borderRadius: 10, alignItems: 'center', justifyContent: 'center' 
  },
  removeBtnText: { color: '#fff', fontWeight: 'bold', fontSize: 10 },
  
  uploadBtn: {
    width: 80, height: 80, borderWidth: 1, borderColor: '#0d6efd', borderStyle: 'dashed',
    borderRadius: 8, alignItems: 'center', justifyContent: 'center', backgroundColor: '#f0f7ff'
  },
  uploadIcon: { fontSize: 24, color: '#0d6efd' },
  uploadText: { fontSize: 10, color: '#0d6efd' },

  // Button Styles
  submitBtn: { 
    backgroundColor: '#0d6efd', padding: 15, borderRadius: 10, alignItems: 'center',
    shadowColor: '#000', shadowOpacity: 0.1, shadowRadius: 5, elevation: 3
  },
  disabledBtn: { backgroundColor: '#a0c4ff' },
  submitBtnText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },

  // Modal Styles
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.5)', justifyContent: 'flex-end' },
  modalContent: { backgroundColor: '#fff', borderTopLeftRadius: 20, borderTopRightRadius: 20, padding: 20, maxHeight: '60%' },
  modalTitle: { fontSize: 18, fontWeight: 'bold', marginBottom: 15, textAlign: 'center' },
  modalItem: { paddingVertical: 15, borderBottomWidth: 1, borderBottomColor: '#eee' },
  modalItemText: { fontSize: 16 },
  closeModalBtn: { marginTop: 20, padding: 15, backgroundColor: '#eee', borderRadius: 10, alignItems: 'center' },
  closeModalText: { fontWeight: 'bold', color: '#333' }
});

export default CreateFeedbackScreen;
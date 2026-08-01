import type { ReportConfig } from './types';
import { formatCurrency, formatKg, formatPercent, formatPlain, formatUsd } from './formatters';

/** Padok ve yem raporları: tüketim, stok durumu, doluluk, maliyet-verimlilik. */
export const pensFeedReports: ReportConfig[] = [
  {
    slug: 'feed-consumption',
    title: 'Yem Tüketim Raporu',
    description:
      'Aralıkta rasyon dönemleri ve padoğun fiilen dolu olduğu günlerden türetilen yem tüketimi, padok/yem tipi bazında.',
    endpoint: '/reports/feed-consumption',
    dateRange: true,
    columns: [
      { key: 'pen_code', label: 'Padok Kodu', width: 'narrow' },
      { key: 'pen_name', label: 'Padok Adı', width: 'narrow' },
      { key: 'feed_item_name', label: 'Yem Ürünü', width: 'narrow' },
      { key: 'feed_type_name', label: 'Yem Tipi', width: 'narrow' },
      { key: 'total_quantity_kg', label: 'Toplam Miktar', format: formatKg, width: 'narrow' },
      { key: 'active_days', label: 'Aktif Gün', width: 'narrow' },
    ],
  },
  {
    slug: 'feed-stock-status',
    title: 'Yem Stok Durumu',
    description:
      'Yem ürünü bazında toplam alım, tüketim, mevcut stok (kg) ve ağırlıklı ortalama maliyetle hesaplanan stok değeri (TL).',
    endpoint: '/reports/feed-stock-status',
    singleDate: true,
    columns: [
      { key: 'feed_item_name', label: 'Yem Ürünü', width: 'narrow' },
      { key: 'feed_type_name', label: 'Yem Tipi', width: 'narrow' },
      { key: 'total_purchased_kg', label: 'Toplam Alım', format: formatKg, width: 'narrow' },
      { key: 'total_consumed_kg', label: 'Toplam Tüketim', format: formatKg, width: 'narrow' },
      { key: 'stock_kg', label: 'Mevcut Stok', format: formatKg, width: 'narrow' },
      { key: 'avg_cost_per_kg_try', label: 'Ort. Maliyet (TL/kg)', format: formatCurrency, width: 'narrow' },
      { key: 'stock_value_try', label: 'Stok Değeri (TL)', format: formatCurrency, width: 'narrow' },
    ],
    rowHighlight: (row) => typeof row.stock_kg === 'number' && row.stock_kg < 0,
  },
  {
    slug: 'pen-occupancy',
    title: 'Padok Doluluk Durumu',
    description: 'Padokların kapasite ve güncel doluluk oranları.',
    endpoint: '/reports/pen-occupancy',
    columns: [
      { key: 'code', label: 'Kod', width: 'narrow' },
      { key: 'name', label: 'Ad', width: 'narrow' },
      { key: 'capacity', label: 'Kapasite', format: formatPlain, width: 'narrow' },
      { key: 'current_count', label: 'Mevcut Sayı', width: 'narrow' },
      { key: 'occupancy_rate', label: 'Doluluk Oranı', format: formatPercent, width: 'narrow' },
    ],
    rowHighlight: (row) => typeof row.occupancy_rate === 'number' && row.occupancy_rate >= 100,
  },
  {
    slug: 'pen-efficiency',
    title: 'Padok Maliyet-Verimlilik Raporu',
    description:
      'Aralıkta padoğa dağıtılan yem (miktar, TL ve TCMB kuruyla USD) ile o padoktaki hayvanların gerçek kilo artışı karşılaştırılır: yem dönüşüm oranı (FCR) ve kg canlı ağırlık başına maliyet.',
    endpoint: '/reports/pen-efficiency',
    dateRange: true,
    defaultRangeDays: 180,
    columns: [
      { key: 'code', label: 'Padok Kodu', width: 'narrow' },
      { key: 'name', label: 'Padok Adı', width: 'narrow' },
      { key: 'total_feed_quantity_kg', label: 'Toplam Yem', format: formatKg, width: 'narrow' },
      { key: 'total_feed_cost_try', label: 'Yem Maliyeti (TL)', format: formatCurrency, width: 'narrow' },
      { key: 'total_feed_cost_usd', label: 'Yem Maliyeti ($)', format: formatUsd, width: 'narrow' },
      { key: 'total_weight_gain_kg', label: 'Toplam Kilo Artışı', format: formatKg, width: 'narrow' },
      { key: 'feed_conversion_ratio', label: 'Yem Dönüşüm Oranı (FCR)', format: formatPlain, width: 'narrow' },
      { key: 'cost_per_kg_gain_try', label: 'Kg Artış Başına Maliyet (TL)', format: formatCurrency, width: 'narrow' },
      { key: 'cost_per_kg_gain_usd', label: 'Kg Artış Başına Maliyet ($)', format: formatUsd, width: 'narrow' },
    ],
  },
];

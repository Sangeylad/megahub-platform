# mcp_server/keyword_tools.py
"""Tools pour les mots-clés - ALIGNÉ SUR VIEWS DJANGO"""

KEYWORD_TOOLS = [
    {
        "name": "search_keywords",
        "description": "Search keywords with ALL advanced filters (aligned with KeywordFilter)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "search_term": {"type": "string", "description": "Search in keyword text"},
                "search_intent": {"type": "string", "enum": ["TOFU", "MOFU", "BOFU"]},
                
                # Volume
                "volume_min": {"type": "integer", "description": "Minimum search volume"},
                "volume_max": {"type": "integer", "description": "Maximum search volume"},
                
                # DA metrics (tous les quartiles)
                "da_min": {"type": "integer", "description": "Min DA minimum"},
                "da_max": {"type": "integer", "description": "Max DA maximum"},
                "da_median": {"type": "integer", "description": "DA median exact"},
                "da_median_min": {"type": "integer", "description": "Min DA median"},
                "da_median_max": {"type": "integer", "description": "Max DA median"},
                "da_q1_min": {"type": "integer", "description": "Min DA Q1"},
                "da_q3_max": {"type": "integer", "description": "Max DA Q3"},
                
                # BL metrics (tous les quartiles)
                "bl_min": {"type": "integer", "description": "Min BL minimum"},
                "bl_max": {"type": "integer", "description": "Max BL maximum"},
                "bl_median": {"type": "integer", "description": "BL median exact"},
                "bl_median_min": {"type": "integer", "description": "Min BL median"},
                "bl_median_max": {"type": "integer", "description": "Max BL median"},
                
                # KD et CPC (avec normalisation)
                "kdifficulty_min": {"type": "number", "description": "Min keyword difficulty"},
                "kdifficulty_max": {"type": "number", "description": "Max keyword difficulty"},
                "cpc_min": {"type": "number", "description": "Min cost per click"},
                "cpc_max": {"type": "number", "description": "Max cost per click"},
                
                # Features booléennes
                "local_pack": {"type": "boolean", "description": "Has local pack"},
                "youtube_videos": {"type": "string", "description": "YouTube videos filter"},
                "has_ppas": {"type": "boolean", "description": "Has People Also Ask"},
                
                # Relations
                "content_type": {"type": "string", "description": "Filter by content type"},
                "in_cocoon": {"type": "integer", "description": "Keywords in specific cocoon"},
                "exclude_page": {"type": "integer", "description": "Exclude keywords from page"},
                
                # Mode vérification d'existence (comme view)
                "keyword_list": {"type": "array", "items": {"type": "string"}, "description": "Check existence of keywords"},
                
                "limit": {"type": "integer", "default": 20, "description": "Max results"}
            },
            "required": ["brand_id"]
        }
    },
    {
        "name": "get_keyword_details",
        "description": "Get detailed keyword info with PPAs and content types",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "keyword_id": {"type": "integer", "description": "Keyword ID"}
            },
            "required": ["brand_id", "keyword_id"]
        }
    },
    {
        "name": "analyze_keyword_performance",
        "description": "Analyze keyword performance with full metrics",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "keyword_ids": {"type": "array", "items": {"type": "integer"}, "description": "List of keyword IDs"},
                "limit": {"type": "integer", "default": 10}
            },
            "required": ["brand_id"]
        }
    },
    {
        "name": "get_ppa_analytics",
        "description": "Get PPA analytics (aligned with PPAAnalyticsView)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "page_id": {"type": "integer", "description": "Filter by page"},
                "website_id": {"type": "integer", "description": "Filter by website"},
                "search": {"type": "string", "description": "Search in PPA questions"},
                "ordering": {"type": "string", "default": "-total_volume", "description": "Order by field"},
                "limit": {"type": "integer", "default": 100}
            },
            "required": ["brand_id"]
        }
    },
    {
        "name": "get_content_types",
        "description": "List all content types",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "search": {"type": "string", "description": "Search in name/description"}
            },
            "required": ["brand_id"]
        }
    }
]

def handle_keyword_tool(tool_name: str, arguments: dict, brand_id: int) -> dict:
    """Handler pour les outils keyword - ALIGNÉ SUR VIEWS DJANGO"""
    try:
        from seo_analyzer.models import Keyword, PPA, ContentType, KeywordContentType
        from business.models import Brand
        from django.db.models import Count, Sum, Avg, Q, F, Cast, FloatField, Value
        from django.db.models.functions import Replace
        
        # Vérifier l'accès à la brand
        try:
            brand = Brand.objects.get(id=brand_id)
        except Brand.DoesNotExist:
            return {'success': False, 'error': f'Brand {brand_id} not found'}
        
        if tool_name == "search_keywords":
            # EXACTEMENT comme KeywordFilter avec TOUTES les annotations
            queryset = Keyword.objects.all()
            
            # ✅ MODE VÉRIFICATION D'EXISTENCE (comme KeywordViewSet.list)
            keyword_list = arguments.get('keyword_list', [])
            if keyword_list:
                existing = queryset.filter(keyword__in=keyword_list).values(
                    'id', 'keyword', 'volume', 'kdifficulty'
                )
                existing_keywords = list(existing)
                existing_texts = [k['keyword'] for k in existing_keywords]
                missing = [k for k in keyword_list if k not in existing_texts]
                
                return {
                    'success': True,
                    'result': {
                        'mode': 'existence_check',
                        'count': len(existing_keywords),
                        'results': existing_keywords,
                        'missing': missing,
                        'checked': len(keyword_list)
                    }
                }
            
            # ✅ FILTRES STANDARD
            search_term = arguments.get('search_term')
            if search_term:
                queryset = queryset.filter(keyword__icontains=search_term)
            
            search_intent = arguments.get('search_intent')
            if search_intent:
                queryset = queryset.filter(search_intent=search_intent)
            
            # Volume
            volume_min = arguments.get('volume_min')
            if volume_min:
                queryset = queryset.filter(volume__gte=volume_min)
            
            volume_max = arguments.get('volume_max')
            if volume_max:
                queryset = queryset.filter(volume__lte=volume_max)
            
            # ✅ MÉTRIQUES DA (tous les quartiles)
            da_min = arguments.get('da_min')
            if da_min:
                queryset = queryset.filter(da_min__gte=da_min)
            
            da_median_min = arguments.get('da_median_min')
            if da_median_min:
                queryset = queryset.filter(da_median__gte=da_median_min)
            
            da_median_max = arguments.get('da_median_max')
            if da_median_max:
                queryset = queryset.filter(da_median__lte=da_median_max)
            
            # ✅ MÉTRIQUES BL (tous les quartiles)
            bl_median_min = arguments.get('bl_median_min')
            if bl_median_min:
                queryset = queryset.filter(bl_median__gte=bl_median_min)
            
            bl_median_max = arguments.get('bl_median_max')
            if bl_median_max:
                queryset = queryset.filter(bl_median__lte=bl_median_max)
            
            # ✅ KD NORMALISÉ (comme KeywordFilter)
            kd_min = arguments.get('kdifficulty_min')
            if kd_min:
                queryset = queryset.annotate(
                    kd_normalized=Cast(
                        Replace(Replace('kdifficulty', Value('%'), Value('')), 
                              Value(','), Value('.')),
                        FloatField()
                    )
                ).filter(kd_normalized__gte=kd_min)
            
            # ✅ CPC NORMALISÉ (comme KeywordFilter)
            cpc_min = arguments.get('cpc_min')
            if cpc_min:
                queryset = queryset.annotate(
                    cpc_normalized=Cast(
                        Replace(Replace(Replace('cpc', Value('€'), Value('')), 
                                      Value(','), Value('.')), 
                               Value(' '), Value('')),
                        FloatField()
                    )
                ).filter(cpc_normalized__gte=cpc_min)
            
            # ✅ FEATURES BOOLÉENNES
            local_pack = arguments.get('local_pack')
            if local_pack is not None:
                queryset = queryset.filter(local_pack=local_pack)
            
            youtube_videos = arguments.get('youtube_videos')
            if youtube_videos:
                queryset = queryset.filter(youtube_videos=youtube_videos)
            
            has_ppas = arguments.get('has_ppas')
            if has_ppas is not None:
                if has_ppas:
                    queryset = queryset.filter(ppa_associations__isnull=False).distinct()
                else:
                    queryset = queryset.filter(ppa_associations__isnull=True)
            
            # ✅ RELATIONS
            content_type = arguments.get('content_type')
            if content_type:
                queryset = queryset.filter(content_type_objects__name__icontains=content_type)
            
            in_cocoon = arguments.get('in_cocoon')
            if in_cocoon:
                queryset = queryset.filter(cocoon_associations__cocoon_id=in_cocoon)
            
            exclude_page = arguments.get('exclude_page')
            if exclude_page:
                queryset = queryset.exclude(keyword_pages__page_id=exclude_page)
            
            # ✅ ANNOTATIONS comme KeywordViewSet
            queryset = queryset.annotate(
                cocoons_count=Count('cocoon_associations', distinct=True),
                pages_count=Count('keyword_pages', distinct=True),
                has_ppas_count=Count('ppa_associations', distinct=True)
            )
            
            limit = arguments.get('limit', 20)
            keywords = queryset[:limit]
            
            return {
                'success': True,
                'result': {
                    'brand_context': {'id': brand.id, 'name': brand.name},
                    'keywords': [
                        {
                            'id': kw.id,
                            'keyword': kw.keyword,
                            'volume': kw.volume,
                            'search_intent': kw.search_intent,
                            'kdifficulty': kw.kdifficulty,
                            'cpc': kw.cpc,
                            'da_median': kw.da_median,
                            'bl_median': kw.bl_median,
                            'local_pack': kw.local_pack,
                            'youtube_videos': kw.youtube_videos,
                            'cocoons_count': kw.cocoons_count,
                            'pages_count': kw.pages_count,
                            'has_ppas': kw.has_ppas_count > 0
                        }
                        for kw in keywords
                    ],
                    'total_matching': queryset.count(),
                    'returned_count': len(keywords),
                    'filters_applied': {
                        'search_term': search_term,
                        'search_intent': search_intent,
                        'volume_range': [volume_min, volume_max],
                        'da_median_range': [da_median_min, da_median_max],
                        'bl_median_range': [bl_median_min, bl_median_max]
                    }
                }
            }
        
        elif tool_name == "get_keyword_details":
            # EXACTEMENT comme KeywordViewSet.retrieve avec préchargement
            keyword_id = arguments.get('keyword_id')
            try:
                keyword = Keyword.objects.prefetch_related(
                    'content_type_objects',
                    'ppa_associations__ppa',
                    'cocoon_associations__cocoon',
                    'keyword_pages__page__website'
                ).get(id=keyword_id)
                
                # PPAs
                ppas = []
                for ppa_assoc in keyword.ppa_associations.all()[:5]:
                    ppas.append({
                        'question': ppa_assoc.ppa.question,
                        'position': ppa_assoc.position
                    })
                
                # Content types
                content_types = [ct.name for ct in keyword.content_type_objects.all()]
                
                # Pages utilisant ce keyword
                pages_using = []
                for page_kw in keyword.keyword_pages.all()[:10]:
                    pages_using.append({
                        'page_id': page_kw.page.id,
                        'page_title': page_kw.page.title,
                        'page_url': page_kw.page.url_path,
                        'website_name': page_kw.page.website.name,
                        'keyword_type': page_kw.keyword_type,
                        'position': page_kw.position
                    })
                
                return {
                    'success': True,
                    'result': {
                        'id': keyword.id,
                        'keyword': keyword.keyword,
                        'volume': keyword.volume,
                        'search_intent': keyword.search_intent,
                        'kdifficulty': keyword.kdifficulty,
                        'cpc': keyword.cpc,
                        'metrics': {
                            'da_min': keyword.da_min,
                            'da_max': keyword.da_max,
                            'da_median': keyword.da_median,
                            'da_q1': keyword.da_q1,
                            'da_q3': keyword.da_q3,
                            'bl_min': keyword.bl_min,
                            'bl_max': keyword.bl_max,
                            'bl_median': keyword.bl_median,
                            'bl_q1': keyword.bl_q1,
                            'bl_q3': keyword.bl_q3
                        },
                        'features': {
                            'youtube_videos': keyword.youtube_videos,
                            'local_pack': keyword.local_pack
                        },
                        'ppas': ppas,
                        'content_types': content_types,
                        'pages_using': pages_using,
                        'usage_stats': {
                            'cocoons_count': keyword.cocoon_associations.count(),
                            'pages_count': keyword.keyword_pages.count()
                        }
                    }
                }
            except Keyword.DoesNotExist:
                return {'success': False, 'error': f'Keyword {keyword_id} not found'}
        
        elif tool_name == "analyze_keyword_performance":
            keyword_ids = arguments.get('keyword_ids', [])
            limit = arguments.get('limit', 10)
            
            if keyword_ids:
                keywords = Keyword.objects.filter(id__in=keyword_ids)
            else:
                # Top keywords par volume comme la view
                keywords = Keyword.objects.filter(volume__isnull=False).order_by('-volume')[:limit]
            
            # Analyses comme dans la view
            total_volume = sum(kw.volume or 0 for kw in keywords)
            avg_volume = total_volume / len(keywords) if keywords else 0
            
            intent_distribution = {}
            for kw in keywords:
                intent = kw.search_intent or 'Unknown'
                intent_distribution[intent] = intent_distribution.get(intent, 0) + 1
            
            return {
                'success': True,
                'result': {
                    'analysis_summary': {
                        'total_keywords': len(keywords),
                        'total_volume': total_volume,
                        'avg_volume': round(avg_volume, 2),
                        'intent_distribution': intent_distribution
                    },
                    'keywords': [
                        {
                            'id': kw.id,
                            'keyword': kw.keyword,
                            'volume': kw.volume,
                            'search_intent': kw.search_intent,
                            'difficulty_score': kw.kdifficulty,
                            'competition_level': (
                                'High' if (kw.da_median or 0) > 60 
                                else 'Medium' if (kw.da_median or 0) > 30 
                                else 'Low'
                            ),
                            'da_median': kw.da_median,
                            'bl_median': kw.bl_median
                        }
                        for kw in keywords
                    ]
                }
            }
        
        elif tool_name == "get_ppa_analytics":
            # EXACTEMENT comme PPAAnalyticsView
            page_id = arguments.get('page_id')
            website_id = arguments.get('website_id')
            search = arguments.get('search', '')
            ordering = arguments.get('ordering', '-total_volume')
            limit = arguments.get('limit', 100)
            
            queryset = PPA.objects.all()
            
            # Filtres
            if search:
                queryset = queryset.filter(question__icontains=search)
            
            if page_id:
                queryset = queryset.filter(
                    keyword_associations__keyword__keyword_pages__page_id=page_id
                ).distinct()
            elif website_id:
                queryset = queryset.filter(
                    keyword_associations__keyword__keyword_pages__page__website_id=website_id
                ).distinct()
            
            # Annotations pour analytics
            queryset = queryset.annotate(
                keywords_count=Count('keyword_associations__keyword', distinct=True),
                total_volume=Sum('keyword_associations__keyword__volume'),
                avg_volume=Avg('keyword_associations__keyword__volume'),
                avg_da_median=Avg('keyword_associations__keyword__da_median'),
                avg_bl_median=Avg('keyword_associations__keyword__bl_median')
            )
            
            # Tri et limitation
            queryset = queryset.order_by(ordering)[:limit]
            
            data = []
            for ppa in queryset:
                data.append({
                    'id': ppa.id,
                    'question': ppa.question,
                    'keywords_count': ppa.keywords_count or 0,
                    'total_volume': ppa.total_volume or 0,
                    'avg_volume': round(ppa.avg_volume or 0, 2),
                    'avg_da_median': round(ppa.avg_da_median or 0, 2),
                    'avg_bl_median': round(ppa.avg_bl_median or 0, 2),
                    'created_at': ppa.created_at
                })
            
            return {
                'success': True,
                'result': {
                    'filters': {
                        'page_id': page_id,
                        'website_id': website_id,
                        'search': search,
                        'ordering': ordering
                    },
                    'count': len(data),
                    'results': data
                }
            }
        
        elif tool_name == "get_content_types":
            # Comme ContentTypeViewSet
            queryset = ContentType.objects.all()
            
            search = arguments.get('search')
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) | Q(description__icontains=search)
                )
            
            queryset = queryset.order_by('name')
            
            return {
                'success': True,
                'result': {
                    'content_types': [
                        {
                            'id': ct.id,
                            'name': ct.name,
                            'description': ct.description
                        }
                        for ct in queryset
                    ],
                    'total_count': queryset.count()
                }
            }
        
        return {'success': False, 'error': f'Unknown keyword tool: {tool_name}'}
        
    except Exception as e:
        return {'success': False, 'error': f'Error in {tool_name}: {str(e)}'}
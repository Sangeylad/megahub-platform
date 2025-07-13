# mcp_server/cocoon_tools.py
"""Tools pour les cocons sémantiques - ALIGNÉ SUR VIEWS DJANGO"""

COCOON_TOOLS = [
    {
        "name": "list_cocoons",
        "description": "List semantic cocoons with advanced filters (aligned with Django CocoonFilter)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "available_for_page": {"type": "integer", "description": "Page ID to check association"},
                "expand_stats": {"type": "boolean", "default": False, "description": "Include extended statistics"},
                "category": {"type": "integer", "description": "Filter by category ID"},
                "category_name": {"type": "string", "description": "Filter by category name"},
                "has_keywords": {"type": "boolean", "description": "Filter cocoons with/without keywords"},
                "has_pages": {"type": "boolean", "description": "Filter cocoons with/without pages"},
                "website": {"type": "integer", "description": "Filter by website ID"},
                "needs_sync": {"type": "boolean", "description": "Filter cocoons needing OpenAI sync"},
                "search": {"type": "string", "description": "Search in name and description"},
                "limit": {"type": "integer", "default": 20, "description": "Max results"}
            },
            "required": ["brand_id"]
        }
    },
    {
        "name": "get_cocoon_details",
        "description": "Get detailed cocoon info with full statistics (aligned with retrieve view)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "cocoon_id": {"type": "integer", "description": "Cocoon ID"}
            },
            "required": ["brand_id", "cocoon_id"]
        }
    },
    {
        "name": "search_cocoons",
        "description": "Search cocoons by name or description",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "search_term": {"type": "string", "description": "Search term"},
                "limit": {"type": "integer", "default": 10}
            },
            "required": ["brand_id", "search_term"]
        }
    },
    {
        "name": "list_cocoon_keywords",
        "description": "List keywords in a cocoon with advanced filters (aligned with CocoonKeywordFilter)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "cocoon_id": {"type": "integer", "description": "Cocoon ID"},
                "search": {"type": "string", "description": "Search in keyword text"},
                "volume_min": {"type": "integer", "description": "Min volume (alias for volume__gte)"},
                "volume_max": {"type": "integer", "description": "Max volume (alias for volume__lte)"},
                "search_intent": {"type": "string", "enum": ["TOFU", "MOFU", "BOFU"]},
                "local_pack": {"type": "boolean", "description": "Has local pack"},
                "youtube_videos": {"type": "string", "description": "Has YouTube videos"},
                "content_type": {"type": "string", "description": "Filter by content type"},
                "kdifficulty_min": {"type": "number", "description": "Min difficulty (alias frontend)"},
                "kdifficulty_max": {"type": "number", "description": "Max difficulty (alias frontend)"},
                "cpc_min": {"type": "number", "description": "Min CPC (alias frontend)"},
                "cpc_max": {"type": "number", "description": "Max CPC (alias frontend)"},
                "da_median_min": {"type": "integer", "description": "Min DA median (alias frontend)"},
                "da_median_max": {"type": "integer", "description": "Max DA median (alias frontend)"},
                "bl_median_min": {"type": "integer", "description": "Min BL median (alias frontend)"},
                "bl_median_max": {"type": "integer", "description": "Max BL median (alias frontend)"},
                "ordering": {"type": "string", "description": "Sort by field (supports all DA/BL quartiles)"},
                "limit": {"type": "integer", "default": 20}
            },
            "required": ["brand_id", "cocoon_id"]
        }
    },
    {
        "name": "get_cocoon_categories",
        "description": "List all cocoon categories with counts",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"}
            },
            "required": ["brand_id"]
        }
    }
]

def handle_cocoon_tool(tool_name: str, arguments: dict, brand_id: int) -> dict:
    """Handler pour les outils cocoon - ALIGNÉ SUR VIEWS DJANGO"""
    try:
        from seo_analyzer.models import SemanticCocoon, CocoonKeyword, CocoonCategory
        from business.models import Brand
        from django.db.models import Count, Q, Sum, Avg, Prefetch
        
        # Vérifier l'accès à la brand
        try:
            brand = Brand.objects.get(id=brand_id)
        except Brand.DoesNotExist:
            return {'success': False, 'error': f'Brand {brand_id} not found'}
        
        if tool_name == "list_cocoons":
            # EXACTEMENT comme CocoonFilter + SemanticCocoonViewSet
            queryset = SemanticCocoon.objects.all()
            
            # ✅ FILTRE available_for_page (CRUCIAL pour interface)
            available_for_page = arguments.get('available_for_page')
            if available_for_page:
                queryset = queryset.annotate(
                    is_associated=Count('pages', filter=Q(pages__id=available_for_page))
                )
            
            # ✅ FILTRES comme CocoonFilter
            category_id = arguments.get('category')
            if category_id:
                queryset = queryset.filter(categories__id=category_id)
            
            category_name = arguments.get('category_name')
            if category_name:
                queryset = queryset.filter(categories__name__icontains=category_name)
            
            has_keywords = arguments.get('has_keywords')
            if has_keywords is not None:
                if has_keywords:
                    queryset = queryset.filter(cocoon_keywords__isnull=False).distinct()
                else:
                    queryset = queryset.filter(cocoon_keywords__isnull=True)
            
            has_pages = arguments.get('has_pages')
            if has_pages is not None:
                if has_pages:
                    queryset = queryset.filter(pages__isnull=False).distinct()
                else:
                    queryset = queryset.filter(pages__isnull=True)
            
            website_id = arguments.get('website')
            if website_id:
                queryset = queryset.filter(pages__website_id=website_id).distinct()
            
            needs_sync = arguments.get('needs_sync')
            if needs_sync:
                queryset = queryset.filter(
                    Q(openai_file_id__isnull=True) | 
                    Q(last_pushed_at__lt=F('updated_at'))
                )
            
            search_term = arguments.get('search')
            if search_term:
                queryset = queryset.filter(
                    Q(name__icontains=search_term) | 
                    Q(description__icontains=search_term)
                )
            
            # ✅ ANNOTATIONS comme SemanticCocoonViewSet
            queryset = queryset.prefetch_related('categories').annotate(
                keywords_count=Count('cocoon_keywords', distinct=True),
                pages_count=Count('pages', distinct=True)
            )
            
            # ✅ STATS ÉTENDUES si demandées
            expand_stats = arguments.get('expand_stats', False)
            if expand_stats:
                queryset = queryset.annotate(
                    total_volume=Sum('cocoon_keywords__keyword__volume')
                )
            
            limit = arguments.get('limit', 20)
            cocoons = queryset[:limit]
            
            result = []
            for cocoon in cocoons:
                cocoon_data = {
                    'id': cocoon.id,
                    'name': cocoon.name,
                    'description': cocoon.description,
                    'keywords_count': cocoon.keywords_count,
                    'pages_count': cocoon.pages_count,
                    'categories': [{'id': cat.id, 'name': cat.name} for cat in cocoon.categories.all()]
                }
                
                # available_for_page result
                if available_for_page:
                    cocoon_data['is_associated'] = cocoon.is_associated
                
                # Stats étendues
                if expand_stats:
                    cocoon_data['total_volume'] = getattr(cocoon, 'total_volume', 0) or 0
                
                result.append(cocoon_data)
            
            return {
                'success': True,
                'result': {
                    'brand_context': {'id': brand.id, 'name': brand.name},
                    'cocoons': result,
                    'total_count': SemanticCocoon.objects.count(),
                    'filters_applied': {
                        'available_for_page': available_for_page,
                        'expand_stats': expand_stats,
                        'search': search_term,
                        'category': category_id,
                        'has_keywords': has_keywords,
                        'has_pages': has_pages
                    }
                }
            }
        
        elif tool_name == "get_cocoon_details":
            # EXACTEMENT comme SemanticCocoonViewSet.retrieve
            cocoon_id = arguments.get('cocoon_id')
            try:
                cocoon = SemanticCocoon.objects.prefetch_related(
                    'categories',
                    'cocoon_keywords__keyword',
                    'pages__website'
                ).get(id=cocoon_id)
                
                # ✅ STATS DÉTAILLÉES comme retrieve view
                intent_stats = cocoon.cocoon_keywords.values(
                    'keyword__search_intent'
                ).annotate(count=Count('id')).order_by('-count')
                
                # Sites web utilisant le cocon (set pour éviter doublons)
                websites_data = {}
                pages_by_website = {}
                
                for page in cocoon.pages.select_related('website'):
                    website_id = page.website.id
                    if website_id not in websites_data:
                        websites_data[website_id] = {
                            'website_id': website_id,
                            'website_name': page.website.name,
                            'pages': []
                        }
                        pages_by_website[website_id] = []
                    
                    pages_by_website[website_id].append({
                        'id': page.id,
                        'title': page.title,
                        'url_path': page.url_path
                    })
                
                # Assembler la structure finale
                for website_id, pages in pages_by_website.items():
                    websites_data[website_id]['pages'] = pages
                
                # Sample keywords (top 10)
                sample_keywords = []
                for ck in cocoon.cocoon_keywords.select_related('keyword')[:10]:
                    sample_keywords.append({
                        'id': ck.keyword.id,
                        'keyword': ck.keyword.keyword,
                        'volume': ck.keyword.volume,
                        'search_intent': ck.keyword.search_intent,
                        'kdifficulty': ck.keyword.kdifficulty
                    })
                
                return {
                    'success': True,
                    'result': {
                        'id': cocoon.id,
                        'name': cocoon.name,
                        'description': cocoon.description,
                        'categories': [{'id': cat.id, 'name': cat.name} for cat in cocoon.categories.all()],
                        'keywords_count': cocoon.cocoon_keywords.count(),
                        'pages_count': cocoon.pages.count(),
                        'sample_keywords': sample_keywords,
                        'pages_using': list(websites_data.values()),
                        'statistics': {
                            'intent_distribution': list(intent_stats),
                            'websites_count': len(websites_data)
                        }
                    }
                }
            except SemanticCocoon.DoesNotExist:
                return {'success': False, 'error': f'Cocoon {cocoon_id} not found'}
        
        elif tool_name == "search_cocoons":
            search_term = arguments.get('search_term', '')
            limit = arguments.get('limit', 10)
            
            cocoons = SemanticCocoon.objects.filter(
                Q(name__icontains=search_term) | 
                Q(description__icontains=search_term)
            ).annotate(
                keywords_count=Count('cocoon_keywords', distinct=True)
            )[:limit]
            
            return {
                'success': True,
                'result': {
                    'search_term': search_term,
                    'cocoons': [
                        {
                            'id': cocoon.id,
                            'name': cocoon.name,
                            'description': cocoon.description,
                            'keywords_count': cocoon.keywords_count
                        }
                        for cocoon in cocoons
                    ],
                    'count': len(cocoons)
                }
            }
        
        elif tool_name == "list_cocoon_keywords":
            # EXACTEMENT comme CocoonKeywordFilter + ordering complet
            cocoon_id = arguments.get('cocoon_id')
            try:
                cocoon = SemanticCocoon.objects.get(id=cocoon_id)
            except SemanticCocoon.DoesNotExist:
                return {'success': False, 'error': f'Cocoon {cocoon_id} not found'}
            
            # Construire queryset avec tous les filtres
            queryset = CocoonKeyword.objects.filter(cocoon=cocoon).select_related('keyword')
            
            # ✅ TOUS LES FILTRES comme CocoonKeywordFilter
            search = arguments.get('search')
            if search:
                queryset = queryset.filter(keyword__keyword__icontains=search)
            
            # Volume (alias frontend)
            volume_min = arguments.get('volume_min')
            if volume_min:
                queryset = queryset.filter(keyword__volume__gte=volume_min)
            
            volume_max = arguments.get('volume_max')
            if volume_max:
                queryset = queryset.filter(keyword__volume__lte=volume_max)
            
            # Search intent
            search_intent = arguments.get('search_intent')
            if search_intent:
                queryset = queryset.filter(keyword__search_intent=search_intent)
            
            # Features
            local_pack = arguments.get('local_pack')
            if local_pack is not None:
                queryset = queryset.filter(keyword__local_pack=local_pack)
            
            youtube_videos = arguments.get('youtube_videos')
            if youtube_videos:
                queryset = queryset.filter(keyword__youtube_videos=youtube_videos)
            
            # Content type
            content_type = arguments.get('content_type')
            if content_type:
                queryset = queryset.filter(keyword__content_type_objects__name__icontains=content_type)
            
            # Métriques (alias frontend comme dans le filter)
            kd_min = arguments.get('kdifficulty_min')
            if kd_min:
                # Normalisation KD (comme dans KeywordFilter)
                from django.db.models import Cast, FloatField, Value
                from django.db.models.functions import Replace
                queryset = queryset.annotate(
                    kd_normalized=Cast(
                        Replace(Replace('keyword__kdifficulty', Value('%'), Value('')), 
                              Value(','), Value('.')),
                        FloatField()
                    )
                ).filter(kd_normalized__gte=kd_min)
            
            # DA median (alias frontend)
            da_median_min = arguments.get('da_median_min')
            if da_median_min:
                queryset = queryset.filter(keyword__da_median__gte=da_median_min)
            
            da_median_max = arguments.get('da_median_max')
            if da_median_max:
                queryset = queryset.filter(keyword__da_median__lte=da_median_max)
            
            # BL median (alias frontend)
            bl_median_min = arguments.get('bl_median_min')
            if bl_median_min:
                queryset = queryset.filter(keyword__bl_median__gte=bl_median_min)
            
            # ✅ ORDERING complet comme CocoonKeywordViewSet
            ordering = arguments.get('ordering', '-keyword__volume')
            valid_orderings = [
                'keyword__keyword', 'keyword__volume', 'keyword__kdifficulty',
                'keyword__da_min', 'keyword__da_max', 'keyword__da_median', 'keyword__da_q1', 'keyword__da_q3',
                'keyword__bl_min', 'keyword__bl_max', 'keyword__bl_median', 'keyword__bl_q1', 'keyword__bl_q3',
                'created_at', 'updated_at'
            ]
            
            if ordering.lstrip('-') in [o.lstrip('-') for o in valid_orderings]:
                queryset = queryset.order_by(ordering)
            
            limit = arguments.get('limit', 20)
            keywords_qs = queryset[:limit]
            
            keywords = []
            for ck in keywords_qs:
                keywords.append({
                    'id': ck.keyword.id,
                    'keyword': ck.keyword.keyword,
                    'volume': ck.keyword.volume,
                    'search_intent': ck.keyword.search_intent,
                    'kdifficulty': ck.keyword.kdifficulty,
                    'da_median': ck.keyword.da_median,
                    'bl_median': ck.keyword.bl_median,
                    'cpc': ck.keyword.cpc,
                    'local_pack': ck.keyword.local_pack,
                    'youtube_videos': ck.keyword.youtube_videos,
                    'created_at': ck.created_at
                })
            
            return {
                'success': True,
                'result': {
                    'cocoon': {'id': cocoon.id, 'name': cocoon.name},
                    'keywords': keywords,
                    'total_in_cocoon': queryset.count(),
                    'returned_count': len(keywords),
                    'filters_applied': {
                        'search': search,
                        'volume_range': [volume_min, volume_max],
                        'search_intent': search_intent,
                        'ordering': ordering
                    }
                }
            }
        
        elif tool_name == "get_cocoon_categories":
            # Comme CocoonCategoryViewSet avec annotations
            categories = CocoonCategory.objects.annotate(
                cocoons_count=Count('cocoons', distinct=True)
            ).order_by('name')
            
            return {
                'success': True,
                'result': {
                    'categories': [
                        {
                            'id': cat.id,
                            'name': cat.name,
                            'description': cat.description,
                            'color': cat.color,
                            'cocoons_count': cat.cocoons_count
                        }
                        for cat in categories
                    ],
                    'total_categories': categories.count()
                }
            }
        
        return {'success': False, 'error': f'Unknown cocoon tool: {tool_name}'}
        
    except Exception as e:
        return {'success': False, 'error': f'Error in {tool_name}: {str(e)}'}
# mcp_server/website_tools.py
"""Tools pour les sites web et pages - ALIGNÉ SUR VIEWS DJANGO + TOOLS MANQUANTS MCP"""

WEBSITE_TOOLS = [
    {
        "name": "list_websites",
        "description": "List websites for a brand with stats",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "search": {"type": "string", "description": "Search in name and URL"}
            },
            "required": ["brand_id"]
        }
    },
    {
        "name": "get_website_structure",
        "description": "Get complete website structure with pages hierarchy",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "website_id": {"type": "integer", "description": "Website ID"}
            },
            "required": ["brand_id", "website_id"]
        }
    },
    {
        "name": "list_pages",
        "description": "List pages with advanced filters (aligned with PageFilter)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "website_id": {"type": "integer", "description": "Filter by website"},
                "parent": {"type": "integer", "description": "Filter by parent page"},
                "search_intent": {"type": "string", "enum": ["TOFU", "MOFU", "BOFU"]},
                "page_type": {"type": "string", "description": "Filter by page type"},
                "has_parent": {"type": "boolean", "description": "Has parent page"},
                "has_children": {"type": "boolean", "description": "Has child pages"},
                "has_keywords": {"type": "boolean", "description": "Has keywords assigned"},
                "has_cocoons": {"type": "boolean", "description": "Has cocoons assigned"},
                "hierarchy_level": {"type": "integer", "description": "Specific hierarchy level"},
                "exclude_from_sitemap": {"type": "boolean", "description": "Excluded from sitemap"},
                "exclude_page_types": {"type": "string", "description": "Exclude page types (comma-separated)"},
                "search": {"type": "string", "description": "Search in title, URL, meta description"},
                "limit": {"type": "integer", "default": 20}
            },
            "required": ["brand_id"]
        }
    },
    {
        "name": "get_page_by_slug",
        "description": "Get page by slug for Next.js (aligned with by_slug action)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "url_path": {"type": "string", "description": "Page URL path"},
                "website_id": {"type": "integer", "description": "Website ID"}
            },
            "required": ["brand_id", "url_path", "website_id"]
        }
    },
    {
        "name": "get_navigation",
        "description": "Get public navigation for website (aligned with navigation action)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "website_id": {"type": "integer", "description": "Website ID"}
            },
            "required": ["brand_id", "website_id"]
        }
    },
    {
        "name": "get_sitemap_stats",
        "description": "Get sitemap statistics (aligned with sitemap_stats action)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "website_id": {"type": "integer", "description": "Website ID"}
            },
            "required": ["brand_id", "website_id"]
        }
    },
    {
        "name": "analyze_page_keywords",
        "description": "Analyze keyword assignments for pages with detailed stats",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "website_id": {"type": "integer", "description": "Website ID"},
                "page_id": {"type": "integer", "description": "Specific page ID (optional)"}
            },
            "required": ["brand_id", "website_id"]
        }
    },
    {
        "name": "list_page_keywords",
        "description": "List page-keyword associations with filters (aligned with PageKeywordFilter)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "page_id": {"type": "integer", "description": "Filter by page"},
                "keyword_id": {"type": "integer", "description": "Filter by keyword"},
                "keyword_type": {"type": "string", "enum": ["primary", "secondary", "anchor"]},
                "is_ai_selected": {"type": "boolean", "description": "AI selected keywords"},
                "source_cocoon": {"type": "integer", "description": "Filter by source cocoon"},
                "limit": {"type": "integer", "default": 20}
            },
            "required": ["brand_id"]
        }
    },
    # 🎯 TOOLS MANQUANTS POUR KeywordSelectorV2
    {
        "name": "get_used_keywords",
        "description": "Get all keywords already used on a website (for AI analysis)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "website_id": {"type": "integer", "description": "Website ID"}
            },
            "required": ["brand_id", "website_id"]
        }
    },
    {
        "name": "get_website_stats",
        "description": "Get website statistics and metrics (for AI context)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "website_id": {"type": "integer", "description": "Website ID"}
            },
            "required": ["brand_id", "website_id"]
        }
    },
    {
        "name": "get_page_details",
        "description": "Get detailed page information with full context (for AI analysis)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "page_id": {"type": "integer", "description": "Page ID"}
            },
            "required": ["brand_id", "page_id"]
        }
    },
    {
        "name": "get_sibling_keywords",
        "description": "Get keywords used by sibling pages (same parent)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "brand_id": {"type": "integer", "description": "Brand ID"},
                "page_id": {"type": "integer", "description": "Page ID to find siblings"}
            },
            "required": ["brand_id", "page_id"]
        }
    }
]

def handle_website_tool(tool_name: str, arguments: dict, brand_id: int) -> dict:
    """Handler pour les outils website - ALIGNÉ SUR VIEWS DJANGO"""
    try:
        from seo_analyzer.models import Website, Page, PageKeyword
        from business.models import Brand
        from django.db.models import Count, Prefetch, Q, Sum, Avg
        from django.utils import timezone
        
        # Vérifier l'accès à la brand
        try:
            brand = Brand.objects.get(id=brand_id)
        except Brand.DoesNotExist:
            return {'success': False, 'error': f'Brand {brand_id} not found'}
        
        if tool_name == "list_websites":
            # EXACTEMENT comme WebsiteViewSet
            queryset = Website.objects.filter(brand=brand)
            
            search = arguments.get('search')
            if search:
                queryset = queryset.filter(
                    Q(name__icontains=search) | Q(url__icontains=search)
                )
            
            # Annotations comme la view
            websites = queryset.select_related('brand').annotate(
                pages_count=Count('pages', distinct=True)
            ).order_by('name')
            
            return {
                'success': True,
                'result': {
                    'brand_id': brand.id,
                    'brand_name': brand.name,
                    'websites': [
                        {
                            'id': website.id,
                            'name': website.name,
                            'url': website.url,
                            'domain_authority': website.domain_authority,
                            'pages_count': website.pages_count,
                            'keywords_count': PageKeyword.objects.filter(page__website=website).count(),
                            'max_competitor_backlinks': website.max_competitor_backlinks,
                            'max_competitor_kd': website.max_competitor_kd
                        }
                        for website in websites
                    ],
                    'total_websites': websites.count()
                }
            }
        
        elif tool_name == "get_website_structure":
            # EXACTEMENT comme website_tools original mais amélioré
            website_id = arguments.get('website_id')
            try:
                website = Website.objects.get(id=website_id, brand=brand)
            except Website.DoesNotExist:
                return {'success': False, 'error': f'Website {website_id} not found or not accessible'}
            
            # Pages hiérarchiques : racines d'abord
            root_pages = website.pages.filter(parent__isnull=True).order_by('title')
            
            def build_page_tree(page):
                """Construit l'arbre hiérarchique d'une page avec stats"""
                return {
                    'id': page.id,
                    'title': page.title,
                    'url_path': page.url_path,
                    'page_type': page.page_type,
                    'search_intent': page.search_intent,
                    'keywords_count': page.page_keywords.count(),
                    'cocoons_count': page.cocoons.count(),
                    'exclude_from_sitemap': page.exclude_from_sitemap,
                    'children': [
                        build_page_tree(child) 
                        for child in page.children.order_by('title')
                    ]
                }
            
            return {
                'success': True,
                'result': {
                    'website': {
                        'id': website.id,
                        'name': website.name,
                        'url': website.url,
                        'domain_authority': website.domain_authority,
                        'brand_name': brand.name
                    },
                    'structure': [build_page_tree(page) for page in root_pages],
                    'total_pages': website.pages.count(),
                    'max_depth': 3  # Limite connue
                }
            }
        
        elif tool_name == "list_pages":
            # EXACTEMENT comme PageFilter + PageViewSet
            queryset = Page.objects.select_related(
                'website__brand', 'parent', 'selected_content_type'
            )
            
            # Filtrer par brand via website
            queryset = queryset.filter(website__brand=brand)
            
            # ✅ TOUS LES FILTRES comme PageFilter
            website_id = arguments.get('website_id')
            if website_id:
                queryset = queryset.filter(website_id=website_id)
            
            parent_id = arguments.get('parent')
            if parent_id:
                queryset = queryset.filter(parent_id=parent_id)
            
            search_intent = arguments.get('search_intent')
            if search_intent:
                queryset = queryset.filter(search_intent=search_intent)
            
            page_type = arguments.get('page_type')
            if page_type:
                queryset = queryset.filter(page_type=page_type)
            
            has_parent = arguments.get('has_parent')
            if has_parent is not None:
                if has_parent:
                    queryset = queryset.filter(parent__isnull=False)
                else:
                    queryset = queryset.filter(parent__isnull=True)
            
            has_children = arguments.get('has_children')
            if has_children is not None:
                if has_children:
                    queryset = queryset.filter(children__isnull=False).distinct()
                else:
                    queryset = queryset.filter(children__isnull=True)
            
            has_keywords = arguments.get('has_keywords')
            if has_keywords is not None:
                if has_keywords:
                    queryset = queryset.filter(page_keywords__isnull=False).distinct()
                else:
                    queryset = queryset.filter(page_keywords__isnull=True)
            
            has_cocoons = arguments.get('has_cocoons')
            if has_cocoons is not None:
                if has_cocoons:
                    queryset = queryset.filter(cocoons__isnull=False).distinct()
                else:
                    queryset = queryset.filter(cocoons__isnull=True)
            
            hierarchy_level = arguments.get('hierarchy_level')
            if hierarchy_level == 1:
                queryset = queryset.filter(parent__isnull=True)
            elif hierarchy_level == 2:
                queryset = queryset.filter(parent__isnull=False, parent__parent__isnull=True)
            elif hierarchy_level == 3:
                queryset = queryset.filter(parent__parent__isnull=False)
            
            exclude_from_sitemap = arguments.get('exclude_from_sitemap')
            if exclude_from_sitemap is not None:
                queryset = queryset.filter(exclude_from_sitemap=exclude_from_sitemap)
            
            # ✅ EXCLUSION DES TYPES comme dans la view
            exclude_page_types = arguments.get('exclude_page_types')
            if exclude_page_types:
                types_to_exclude = [t.strip() for t in exclude_page_types.split(',') if t.strip()]
                if types_to_exclude:
                    queryset = queryset.exclude(page_type__in=types_to_exclude)
            
            search = arguments.get('search')
            if search:
                queryset = queryset.filter(
                    Q(title__icontains=search) | 
                    Q(url_path__icontains=search) | 
                    Q(meta_description__icontains=search)
                )
            
            # ✅ ANNOTATIONS comme PageViewSet
            queryset = queryset.annotate(
                keywords_count=Count('page_keywords', distinct=True),
                children_count=Count('children', distinct=True)
            )
            
            limit = arguments.get('limit', 20)
            pages = queryset[:limit]
            
            return {
                'success': True,
                'result': {
                    'brand_context': {'id': brand.id, 'name': brand.name},
                    'pages': [
                        {
                            'id': page.id,
                            'title': page.title,
                            'url_path': page.url_path,
                            'page_type': page.page_type,
                            'search_intent': page.search_intent,
                            'website_id': page.website.id,
                            'website_name': page.website.name,
                            'parent_id': page.parent.id if page.parent else None,
                            'parent_title': page.parent.title if page.parent else None,
                            'keywords_count': page.keywords_count,
                            'children_count': page.children_count,
                            'exclude_from_sitemap': page.exclude_from_sitemap,
                            'meta_description': page.meta_description
                        }
                        for page in pages
                    ],
                    'total_matching': queryset.count(),
                    'returned_count': len(pages),
                    'filters_applied': {
                        'website_id': website_id,
                        'search': search,
                        'page_type': page_type,
                        'has_keywords': has_keywords,
                        'hierarchy_level': hierarchy_level
                    }
                }
            }
        
        elif tool_name == "get_page_by_slug":
            # EXACTEMENT comme PageViewSet.by_slug action
            url_path = arguments.get('url_path')
            website_id = arguments.get('website_id')
            
            try:
                # Vérifier que le website appartient à la brand
                website = Website.objects.get(id=website_id, brand=brand)
                
                # Requête optimisée comme la view
                page = Page.objects.select_related(
                    'website', 
                    'website__brand', 
                    'parent',
                    'selected_content_type'
                ).prefetch_related(
                    'children',
                    'page_keywords__keyword',
                    'page_keywords__source_cocoon',
                    'cocoons'
                ).get(
                    url_path=url_path,
                    website_id=website_id
                )
                
                # Vérifier publication si content exists
                if hasattr(page, 'content'):
                    if page.content.status != 'published':
                        return {'success': False, 'error': 'Page not published'}
                
                # Construire la réponse comme le serializer
                children = []
                for child in page.children.all():
                    children.append({
                        'id': child.id,
                        'title': child.title,
                        'url_path': child.url_path,
                        'page_type': child.page_type
                    })
                
                keywords = []
                for pk in page.page_keywords.all():
                    keywords.append({
                        'id': pk.keyword.id,
                        'keyword': pk.keyword.keyword,
                        'keyword_type': pk.keyword_type,
                        'position': pk.position,
                        'volume': pk.keyword.volume,
                        'is_ai_selected': pk.is_ai_selected
                    })
                
                return {
                    'success': True,
                    'result': {
                        'id': page.id,
                        'title': page.title,
                        'url_path': page.url_path,
                        'meta_description': page.meta_description,
                        'page_type': page.page_type,
                        'search_intent': page.search_intent,
                        'website': {
                            'id': website.id,
                            'name': website.name,
                            'url': website.url
                        },
                        'parent': {
                            'id': page.parent.id,
                            'title': page.parent.title,
                            'url_path': page.parent.url_path
                        } if page.parent else None,
                        'children': children,
                        'keywords': keywords,
                        'cocoons': [
                            {'id': c.id, 'name': c.name} 
                            for c in page.cocoons.all()
                        ]
                    }
                }
                
            except Website.DoesNotExist:
                return {'success': False, 'error': f'Website {website_id} not found or not accessible'}
            except Page.DoesNotExist:
                return {'success': False, 'error': f'Page {url_path} not found or not published'}
        
        elif tool_name == "get_navigation":
            # EXACTEMENT comme PageViewSet.navigation action
            website_id = arguments.get('website_id')
            
            try:
                website = Website.objects.get(id=website_id, brand=brand)
            except Website.DoesNotExist:
                return {'success': False, 'error': f'Website {website_id} not found or not accessible'}
            
            # ✅ PAGES À EXCLURE comme dans la view
            blog_template_urls = [
                '/blog', '/blog/', '/blog/categorie-blog', '/blog/categorie-blog/',
                '/blog/article-de-blog', '/blog/article-de-blog/'
            ]
            
            # Pages niveau 1 avec enfants niveau 2
            level_1_pages = Page.objects.filter(
                website_id=website_id,
                parent__isnull=True,
                exclude_from_sitemap=False
            ).exclude(
                Q(page_type__in=['blog', 'blog_category']) |
                Q(url_path__in=blog_template_urls) |
                Q(url_path='/') |
                Q(url_path='/')
            ).select_related('website').prefetch_related(
                Prefetch(
                    'children',
                    queryset=Page.objects.filter(
                        exclude_from_sitemap=False
                    ).exclude(
                        Q(page_type__in=['blog', 'blog_category']) |
                        Q(url_path__in=blog_template_urls)
                    ).order_by('title'),
                    to_attr='nav_children'
                )
            ).order_by('title')
            
            navigation = []
            
            # Ajouter les pages normales
            for page in level_1_pages:
                nav_item = {
                    'id': page.id,
                    'title': page.title,
                    'url_path': page.url_path,
                    'page_type': page.page_type,
                    'children': [],
                    'is_dynamic_blog': False
                }
                
                # Enfants niveau 2
                for child in page.nav_children:
                    nav_item['children'].append({
                        'id': child.id,
                        'title': child.title,
                        'url_path': child.url_path,
                        'page_type': child.page_type,
                        'is_dynamic_blog': False
                    })
                
                navigation.append(nav_item)
            
            # ✅ AJOUTER LE BLOG EN DERNIER (si disponible)
            try:
                from ..models.blog_models import BlogConfig
                
                blog_config = BlogConfig.objects.get(website_id=website_id)
                
                blog_nav_item = {
                    'id': f'blog_{blog_config.id}',
                    'title': blog_config.blog_name,
                    'url_path': blog_config.get_blog_base_url(),
                    'children': [],
                    'is_dynamic_blog': True,
                    'blog_config': {
                        'slug': blog_config.blog_slug,
                        'name': blog_config.blog_name,
                        'description': blog_config.blog_description
                    }
                }
                
                navigation.append(blog_nav_item)
                
            except (ImportError, Exception):
                # BlogConfig pas disponible ou pas configuré
                pass
            
            return {
                'success': True,
                'result': {
                    'navigation': navigation,
                    'website_id': website_id,
                    'website_name': website.name,
                    'total_items': len(navigation),
                    'total_level_2': sum(len(item['children']) for item in navigation),
                    'has_dynamic_blog': any(item.get('is_dynamic_blog', False) for item in navigation),
                    'generated_at': timezone.now()
                }
            }
        
        elif tool_name == "get_sitemap_stats":
            # EXACTEMENT comme PageViewSet.sitemap_stats action
            website_id = arguments.get('website_id')
            
            try:
                website = Website.objects.get(id=website_id, brand=brand)
            except Website.DoesNotExist:
                return {'success': False, 'error': f'Website {website_id} not found or not accessible'}
            
            queryset = Page.objects.filter(website_id=website_id)
            
            # Stats globales
            total_pages = queryset.count()
            excluded_count = queryset.filter(exclude_from_sitemap=True).count()
            
            # Stats par type
            by_type = dict(
                queryset.filter(exclude_from_sitemap=False)
                .values('page_type')
                .annotate(count=Count('id'))
                .values_list('page_type', 'count')
            )
            
            return {
                'success': True,
                'result': {
                    'website_id': website_id,
                    'website_name': website.name,
                    'total_pages': total_pages,
                    'included_in_sitemap': total_pages - excluded_count,
                    'excluded_from_sitemap': excluded_count,
                    'by_type': by_type
                }
            }
        
        elif tool_name == "analyze_page_keywords":
            # AMÉLIORATION de l'analyse existante
            website_id = arguments.get('website_id')
            page_id = arguments.get('page_id')
            
            try:
                website = Website.objects.get(id=website_id, brand=brand)
            except Website.DoesNotExist:
                return {'success': False, 'error': f'Website {website_id} not found or not accessible'}
            
            if page_id:
                # Analyse d'une page spécifique
                try:
                    page = Page.objects.get(id=page_id, website=website)
                except Page.DoesNotExist:
                    return {'success': False, 'error': f'Page {page_id} not found'}
                
                page_keywords = page.page_keywords.select_related('keyword').order_by('position')
                
                return {
                    'success': True,
                    'result': {
                        'page': {
                            'id': page.id,
                            'title': page.title,
                            'url_path': page.url_path,
                            'page_type': page.page_type,
                            'search_intent': page.search_intent
                        },
                        'keywords': [
                            {
                                'keyword_id': pk.keyword.id,
                                'keyword': pk.keyword.keyword,
                                'type': pk.keyword_type,
                                'position': pk.position,
                                'volume': pk.keyword.volume,
                                'search_intent': pk.keyword.search_intent,
                                'is_ai_selected': pk.is_ai_selected,
                                'source_cocoon': pk.source_cocoon.name if pk.source_cocoon else None
                            }
                            for pk in page_keywords
                        ],
                        'keyword_distribution': {
                            'primary': page_keywords.filter(keyword_type='primary').count(),
                            'secondary': page_keywords.filter(keyword_type='secondary').count(),
                            'anchor': page_keywords.filter(keyword_type='anchor').count()
                        }
                    }
                }
            else:
                # Analyse de tout le site
                pages_with_keywords = Page.objects.filter(
                    website=website,
                    page_keywords__isnull=False
                ).distinct()
                
                pages_without_keywords = website.pages.filter(
                    page_keywords__isnull=True
                ).count()
                
                # Stats par type de mot-clé
                total_primary = PageKeyword.objects.filter(
                    page__website=website, 
                    keyword_type='primary'
                ).count()
                
                total_secondary = PageKeyword.objects.filter(
                    page__website=website, 
                    keyword_type='secondary'
                ).count()
                
                total_anchor = PageKeyword.objects.filter(
                    page__website=website, 
                    keyword_type='anchor'
                ).count()
                
                return {
                    'success': True,
                    'result': {
                        'website': {
                            'id': website.id,
                            'name': website.name,
                            'total_pages': website.pages.count()
                        },
                        'keyword_coverage': {
                            'pages_with_keywords': pages_with_keywords.count(),
                            'pages_without_keywords': pages_without_keywords,
                            'coverage_percentage': round(
                                (pages_with_keywords.count() / website.pages.count()) * 100, 2
                            ) if website.pages.count() > 0 else 0
                        },
                        'keyword_distribution': {
                            'total_primary': total_primary,
                            'total_secondary': total_secondary,
                            'total_anchor': total_anchor,
                            'ai_selected': PageKeyword.objects.filter(
                                page__website=website, 
                                is_ai_selected=True
                            ).count()
                        },
                        'pages_needing_keywords': [
                            {
                                'id': page.id,
                                'title': page.title,
                                'page_type': page.page_type,
                                'url_path': page.url_path
                            }
                            for page in website.pages.filter(page_keywords__isnull=True)[:10]
                        ]
                    }
                }
        
        elif tool_name == "list_page_keywords":
            # EXACTEMENT comme PageKeywordFilter + PageKeywordViewSet
            queryset = PageKeyword.objects.select_related(
                'page__website',
                'keyword',
                'source_cocoon'
            )
            
            # Filtrer par brand via page->website
            queryset = queryset.filter(page__website__brand=brand)
            
            # ✅ FILTRES comme PageKeywordFilter
            page_id = arguments.get('page_id')
            if page_id:
                queryset = queryset.filter(page_id=page_id)
            
            keyword_id = arguments.get('keyword_id')
            if keyword_id:
                queryset = queryset.filter(keyword_id=keyword_id)
            
            keyword_type = arguments.get('keyword_type')
            if keyword_type:
                queryset = queryset.filter(keyword_type=keyword_type)
            
            is_ai_selected = arguments.get('is_ai_selected')
            if is_ai_selected is not None:
                queryset = queryset.filter(is_ai_selected=is_ai_selected)
            
            source_cocoon = arguments.get('source_cocoon')
            if source_cocoon:
                queryset = queryset.filter(source_cocoon_id=source_cocoon)
            
            # Préchargement des PPAs comme dans la view
            queryset = queryset.prefetch_related(
                'keyword__ppa_associations__ppa',
                'keyword__content_type_objects'
            )
            
            limit = arguments.get('limit', 20)
            page_keywords = queryset[:limit]
            
            return {
                'success': True,
                'result': {
                    'brand_context': {'id': brand.id, 'name': brand.name},
                    'page_keywords': [
                        {
                            'id': pk.id,
                            'page': {
                                'id': pk.page.id,
                                'title': pk.page.title,
                                'url_path': pk.page.url_path,
                                'website_name': pk.page.website.name
                            },
                            'keyword': {
                                'id': pk.keyword.id,
                                'keyword': pk.keyword.keyword,
                                'volume': pk.keyword.volume,
                                'search_intent': pk.keyword.search_intent
                            },
                            'keyword_type': pk.keyword_type,
                            'position': pk.position,
                            'is_ai_selected': pk.is_ai_selected,
                            'source_cocoon': {
                                'id': pk.source_cocoon.id,
                                'name': pk.source_cocoon.name
                            } if pk.source_cocoon else None,
                            'created_at': pk.created_at
                        }
                        for pk in page_keywords
                    ],
                    'total_matching': queryset.count(),
                    'returned_count': len(page_keywords),
                    'filters_applied': {
                        'page_id': page_id,
                        'keyword_id': keyword_id,
                        'keyword_type': keyword_type,
                        'is_ai_selected': is_ai_selected
                    }
                }
            }
        
        # 🎯 TOOLS MANQUANTS POUR KeywordSelectorV2
        
        elif tool_name == "get_used_keywords":
            """Récupère tous les mots-clés déjà utilisés sur un site (pour éviter la cannibalisation)"""
            website_id = arguments.get('website_id')
            
            try:
                website = Website.objects.get(id=website_id, brand=brand)
            except Website.DoesNotExist:
                return {'success': False, 'error': f'Website {website_id} not found or not accessible'}
            
            # Tous les mots-clés utilisés sur le site
            used_keywords = PageKeyword.objects.filter(
                page__website=website
            ).select_related('keyword', 'page').order_by('keyword__keyword')
            
            keywords_list = []
            for pk in used_keywords:
                keywords_list.append({
                    'keyword_id': pk.keyword.id,
                    'keyword': pk.keyword.keyword,
                    'volume': pk.keyword.volume,
                    'keyword_type': pk.keyword_type,
                    'page_id': pk.page.id,
                    'page_title': pk.page.title,
                    'page_url': pk.page.url_path
                })
            
            # Stats d'utilisation
            stats = {
                'total_keywords_used': used_keywords.count(),
                'unique_keywords': used_keywords.values('keyword_id').distinct().count(),
                'primary_keywords': used_keywords.filter(keyword_type='primary').count(),
                'secondary_keywords': used_keywords.filter(keyword_type='secondary').count(),
                'anchor_keywords': used_keywords.filter(keyword_type='anchor').count()
            }
            
            return {
                'success': True,
                'result': {
                    'website': {
                        'id': website.id,
                        'name': website.name,
                        'url': website.url
                    },
                    'keywords': keywords_list,
                    'stats': stats
                }
            }
        
        elif tool_name == "get_website_stats":
            """Récupère les statistiques d'un site pour contexte IA"""
            website_id = arguments.get('website_id')
            
            try:
                website = Website.objects.get(id=website_id, brand=brand)
            except Website.DoesNotExist:
                return {'success': False, 'error': f'Website {website_id} not found or not accessible'}
            
            # Stats générales
            total_pages = website.pages.count()
            pages_with_keywords = website.pages.filter(page_keywords__isnull=False).distinct().count()
            pages_without_keywords = total_pages - pages_with_keywords
            
            # Stats par type de page
            page_type_stats = {}
            for page_type in website.pages.values_list('page_type', flat=True).distinct():
                count = website.pages.filter(page_type=page_type).count()
                with_keywords = website.pages.filter(
                    page_type=page_type, 
                    page_keywords__isnull=False
                ).distinct().count()
                page_type_stats[page_type] = {
                    'total': count,
                    'with_keywords': with_keywords,
                    'without_keywords': count - with_keywords
                }
            
            # Stats par intention de recherche
            intent_stats = {}
            for intent in ['TOFU', 'MOFU', 'BOFU']:
                count = website.pages.filter(search_intent=intent).count()
                intent_stats[intent] = count
            
            # Stats par niveau hiérarchique
            hierarchy_stats = {
                'level_1': website.pages.filter(parent__isnull=True).count(),
                'level_2': website.pages.filter(
                    parent__isnull=False, 
                    parent__parent__isnull=True
                ).count(),
                'level_3': website.pages.filter(parent__parent__isnull=False).count()
            }
            
            # Métriques SEO du site
            seo_metrics = {
                'domain_authority': website.domain_authority,
                'max_competitor_backlinks': website.max_competitor_backlinks,
                'max_competitor_kd': website.max_competitor_kd
            }
            
            # Pages problématiques (sans mots-clés par type)
            problematic_pages = []
            for page in website.pages.filter(page_keywords__isnull=True)[:10]:
                problematic_pages.append({
                    'id': page.id,
                    'title': page.title,
                    'url_path': page.url_path,
                    'page_type': page.page_type,
                    'search_intent': page.search_intent,
                    'hierarchy_level': page.get_hierarchy_level() if hasattr(page, 'get_hierarchy_level') else 1
                })
            
            return {
                'success': True,
                'result': {
                    'website': {
                        'id': website.id,
                        'name': website.name,
                        'url': website.url,
                        'brand_name': brand.name
                    },
                    'coverage_stats': {
                        'total_pages': total_pages,
                        'pages_with_keywords': pages_with_keywords,
                        'pages_without_keywords': pages_without_keywords,
                        'coverage_percentage': round((pages_with_keywords / total_pages) * 100, 2) if total_pages > 0 else 0
                    },
                    'page_type_distribution': page_type_stats,
                    'search_intent_distribution': intent_stats,
                    'hierarchy_distribution': hierarchy_stats,
                    'seo_metrics': seo_metrics,
                    'problematic_pages': problematic_pages
                }
            }
        
        elif tool_name == "get_page_details":
            """Récupère les détails complets d'une page pour analyse IA"""
            page_id = arguments.get('page_id')
            
            try:
                page = Page.objects.select_related(
                    'website__brand',
                    'parent',
                    'selected_content_type'
                ).prefetch_related(
                    'children',
                    'page_keywords__keyword',
                    'page_keywords__source_cocoon',
                    'cocoons'
                ).get(id=page_id, website__brand=brand)
                
                # Informations hiérarchiques
                hierarchy_info = {
                    'level': 1,  # Par défaut niveau 1
                    'parent': None,
                    'children': [],
                    'siblings': []
                }
                
                if page.parent:
                    if page.parent.parent:
                        hierarchy_info['level'] = 3
                    else:
                        hierarchy_info['level'] = 2
                    
                    hierarchy_info['parent'] = {
                        'id': page.parent.id,
                        'title': page.parent.title,
                        'url_path': page.parent.url_path
                    }
                    
                    # Pages sœurs (même parent)
                    siblings = Page.objects.filter(
                        parent=page.parent
                    ).exclude(id=page.id).values('id', 'title', 'url_path')
                    hierarchy_info['siblings'] = list(siblings)
                
                # Pages enfants
                children = []
                for child in page.children.all():
                    children.append({
                        'id': child.id,
                        'title': child.title,
                        'url_path': child.url_path,
                        'page_type': child.page_type
                    })
                hierarchy_info['children'] = children
                
                # Mots-clés actuels
                current_keywords = []
                for pk in page.page_keywords.all():
                    current_keywords.append({
                        'keyword_id': pk.keyword.id,
                        'keyword': pk.keyword.keyword,
                        'type': pk.keyword_type,
                        'position': pk.position,
                        'volume': pk.keyword.volume,
                        'is_ai_selected': pk.is_ai_selected
                    })
                
                # Cocons associés
                associated_cocoons = []
                for cocoon in page.cocoons.all():
                    associated_cocoons.append({
                        'id': cocoon.id,
                        'name': cocoon.name,
                        'keywords_count': cocoon.cocoon_keywords.count()
                    })
                
                return {
                    'success': True,
                    'result': {
                        'page': {
                            'id': page.id,
                            'title': page.title,
                            'url_path': page.url_path,
                            'meta_description': page.meta_description,
                            'page_type': page.page_type,
                            'search_intent': page.search_intent,
                            'exclude_from_sitemap': page.exclude_from_sitemap
                        },
                        'website': {
                            'id': page.website.id,
                            'name': page.website.name,
                            'domain_authority': page.website.domain_authority
                        },
                        'hierarchy': hierarchy_info,
                        'current_keywords': current_keywords,
                        'associated_cocoons': associated_cocoons,
                        'has_content': hasattr(page, 'content')
                    }
                }
                
            except Page.DoesNotExist:
                return {'success': False, 'error': f'Page {page_id} not found or not accessible'}
        
        elif tool_name == "get_sibling_keywords":
            """Récupère les mots-clés utilisés par les pages sœurs (même parent)"""
            page_id = arguments.get('page_id')
            
            try:
                page = Page.objects.select_related('parent').get(
                    id=page_id, 
                    website__brand=brand
                )
                
                if not page.parent:
                    return {
                        'success': True,
                        'result': {
                            'page_id': page_id,
                            'message': 'Page has no parent, therefore no siblings',
                            'keywords': []
                        }
                    }
                
                # Mots-clés des pages sœurs
                sibling_keywords = PageKeyword.objects.filter(
                    page__parent=page.parent
                ).exclude(
                    page_id=page_id
                ).select_related('keyword', 'page').order_by('keyword__keyword')
                
                keywords_list = []
                for pk in sibling_keywords:
                    keywords_list.append({
                        'keyword_id': pk.keyword.id,
                        'keyword': pk.keyword.keyword,
                        'volume': pk.keyword.volume,
                        'keyword_type': pk.keyword_type,
                        'sibling_page_id': pk.page.id,
                        'sibling_page_title': pk.page.title,
                        'sibling_page_url': pk.page.url_path
                    })
                
                return {
                    'success': True,
                    'result': {
                        'page_id': page_id,
                        'parent_page': {
                            'id': page.parent.id,
                            'title': page.parent.title
                        },
                        'keywords': keywords_list,
                        'total_sibling_keywords': len(keywords_list)
                    }
                }
                
            except Page.DoesNotExist:
                return {'success': False, 'error': f'Page {page_id} not found or not accessible'}
        
        return {'success': False, 'error': f'Unknown website tool: {tool_name}'}
        
    except Exception as e:
        return {'success': False, 'error': f'Error in {tool_name}: {str(e)}'}
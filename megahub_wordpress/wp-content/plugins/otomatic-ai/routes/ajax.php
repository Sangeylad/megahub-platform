<?php

use OtomaticAi\Controllers\AuthController;
use OtomaticAi\Controllers\BuyerPersonaController;
use OtomaticAi\Controllers\DashboardController;
use OtomaticAi\Controllers\GenerateKeywordController;
use OtomaticAi\Controllers\GenerateRequestController;
use OtomaticAi\Controllers\GenerateStructureController;
use OtomaticAi\Controllers\RewriteStructureController;
use OtomaticAi\Controllers\HelpCenterController;
use OtomaticAi\Controllers\ImageGeneratorController;
use OtomaticAi\Controllers\KeywordController;
use OtomaticAi\Controllers\PersonaController;
use OtomaticAi\Controllers\ProjectController;
use OtomaticAi\Controllers\PresetController;
use OtomaticAi\Controllers\PublicationController;
use OtomaticAi\Controllers\RequestController;
use OtomaticAi\Controllers\RewriteRequestController;
use OtomaticAi\Controllers\Settings\ApiController;
use OtomaticAi\Controllers\Linking\AutomaticPagesController;
use OtomaticAi\Controllers\Linking\AutomaticPostsController;
use OtomaticAi\Controllers\Linking\ManualController;
use OtomaticAi\Controllers\PricingPlanController;
use OtomaticAi\Controllers\TemplateController;
use OtomaticAi\Controllers\UsageController;
use OtomaticAi\Controllers\WordpressController;
use OtomaticAi\Utils\Route;

// auth
Route::ajax("auth_login", AuthController::class, 'login');
Route::ajax("auth_logout", AuthController::class, 'logout');
Route::ajax("auth_domain", AuthController::class, 'domain');
Route::ajax("auth_required_settings", AuthController::class, 'requiredSettings');
Route::ajax("auth_enable_premium", AuthController::class, 'enablePremium');
Route::ajax("auth_disable_premium", AuthController::class, 'disablePremium');

// wordpress
Route::ajax("wordpress_users", WordpressController::class, 'users');
Route::ajax("wordpress_templates", WordpressController::class, 'templates');
Route::ajax("wordpress_statuses", WordpressController::class, 'statuses');
Route::ajax("wordpress_categories", WordpressController::class, 'categories');
Route::ajax("wordpress_tags", WordpressController::class, 'tags');
Route::ajax("wordpress_user_roles", WordpressController::class, 'userRoles');
Route::ajax("wordpress_post_types", WordpressController::class, 'postTypes');

// presets
Route::ajax("presets_index", PresetController::class, 'index');
Route::ajax("presets_show", PresetController::class, 'show');
Route::ajax("presets_store", PresetController::class, 'store');
Route::ajax("presets_update", PresetController::class, 'update');
Route::ajax("presets_destroy", PresetController::class, 'destroy');

// personas
Route::ajax("personas_index", PersonaController::class, 'index');
Route::ajax("personas_store", PersonaController::class, 'store');
Route::ajax("personas_edit", PersonaController::class, 'edit');
Route::ajax("personas_destroy", PersonaController::class, 'destroy');
Route::ajax("personas_update_profil", PersonaController::class, 'updateProfil');
Route::ajax("personas_update_biography", PersonaController::class, 'updateBiography');
Route::ajax("personas_update_avatar", PersonaController::class, 'updateAvatar');
Route::ajax("personas_validate_language_step", PersonaController::class, 'validateLanguageStep');
Route::ajax("personas_validate_user_step", PersonaController::class, 'validateUserStep');
Route::ajax("personas_validate_profil_step", PersonaController::class, 'validateProfilStep');
Route::ajax("personas_generate_biography", PersonaController::class, 'generateBiography');
Route::ajax("personas_validate_biography_step", PersonaController::class, 'validateBiographyStep');
Route::ajax("personas_generate_avatar", PersonaController::class, 'generateAvatar');

// buyer persona
Route::ajax('buyer_personas_generate', BuyerPersonaController::class, 'generate');
Route::ajax('buyer_personas_generate_from_project', BuyerPersonaController::class, 'generateFromProject');

// projects
Route::ajax("projects_index", ProjectController::class, 'index');
Route::ajax("projects_show", ProjectController::class, 'show');
Route::ajax("projects_enable", ProjectController::class, 'enable');
Route::ajax("projects_disable", ProjectController::class, 'disable');
Route::ajax("projects_destroy", ProjectController::class, 'destroy');
Route::ajax("projects_store", ProjectController::class, 'store');
Route::ajax("projects_update", ProjectController::class, 'update');
Route::ajax("project_validate_requests_keyword_step", ProjectController::class, 'validateRequestsKeywordStep');
Route::ajax("project_validate_requests_step", ProjectController::class, 'validateRequestsStep');
Route::ajax("project_validate_content_step", ProjectController::class, 'validateContentStep');
Route::ajax("project_validate_planning_step", ProjectController::class, 'validatePlanningStep');

// requests
Route::ajax("requests_generate", GenerateRequestController::class);
Route::ajax("requests_rewrite", RewriteRequestController::class);
Route::ajax("requests_trends", RequestController::class, 'trends');
Route::ajax("requests_suggestions", RequestController::class, 'suggestions');
Route::ajax("requests_details", RequestController::class, 'details');
Route::ajax("requests_metrics", KeywordController::class, 'metrics');

// structure
Route::ajax("structure_generate", GenerateStructureController::class, 'generateStructure');
Route::ajax("structure_generate_h2", GenerateStructureController::class, 'generateH2');
Route::ajax("structure_generate_h3", GenerateStructureController::class, 'generateH3');
Route::ajax("structure_rewrite", RewriteStructureController::class);

// keywords
Route::ajax("keywords_generate", GenerateKeywordController::class);

// publications
Route::ajax("publications_index", PublicationController::class, 'index');
Route::ajax("publications_latest_published", PublicationController::class, 'latestPublished');
Route::ajax("publications_next_published", PublicationController::class, 'nextPublished');
Route::ajax("publications_store", PublicationController::class, 'store');
Route::ajax("publications_publish", PublicationController::class, 'publish');
Route::ajax("publications_retry", PublicationController::class, 'retry');
Route::ajax("publications_regenerate", PublicationController::class, 'regenerate');
Route::ajax("publications_bulk_regenerate", PublicationController::class, 'bulkRegenerate');
Route::ajax("publications_bulk_publish", PublicationController::class, 'bulkPublish');
Route::ajax("publications_destroy", PublicationController::class, 'destroy');
Route::ajax("publications_bulk_destroy", PublicationController::class, 'bulkDestroy');

// settings
Route::ajax("settings_api_index", ApiController::class, 'index');
Route::ajax("settings_api_set_openai", ApiController::class, 'setOpenAI');
Route::ajax("settings_api_update_openai", ApiController::class, 'updateOpenAI');
Route::ajax("settings_api_update_mistral_ai", ApiController::class, 'updateMistralAi');
Route::ajax("settings_api_update_groq", ApiController::class, 'updateGroq');
Route::ajax("settings_api_update_stability_ai", ApiController::class, 'updateStabilityAI');
Route::ajax("settings_api_update_unsplash", ApiController::class, 'updateUnsplash');
Route::ajax("settings_api_update_pexels", ApiController::class, 'updatePexels');
Route::ajax("settings_api_update_pixabay", ApiController::class, 'updatePixabay');
Route::ajax("settings_api_update_haloscan", ApiController::class, 'updateHaloscan');

// linking
Route::ajax("linking_automatic_posts_index", AutomaticPostsController::class, 'index');
Route::ajax("linking_automatic_posts_update_settings", AutomaticPostsController::class, 'updateSettings');
Route::ajax("linking_automatic_posts_update_template", AutomaticPostsController::class, 'updateTemplate');
Route::ajax("linking_automatic_pages_index", AutomaticPagesController::class, 'index');
Route::ajax("linking_automatic_pages_update_settings", AutomaticPagesController::class, 'updateSettings');
Route::ajax("linking_automatic_pages_update_template", AutomaticPagesController::class, 'updateTemplate');
Route::ajax("linking_manual_index", ManualController::class, 'index');
Route::ajax("linking_manual_store", ManualController::class, 'store');
Route::ajax("linking_manual_update", ManualController::class, 'update');
Route::ajax("linking_manual_destroy", ManualController::class, 'destroy');
Route::ajax("linking_manual_generate_keywords", ManualController::class, 'generateKeywords');
Route::ajax("linking_manual_search_posts", ManualController::class, 'searchPosts');

// templates
Route::ajax("templates_index", TemplateController::class, 'index');
Route::ajax("templates_store", TemplateController::class, 'store');
Route::ajax("templates_destroy", TemplateController::class, 'destroy');
Route::ajax("templates_export", TemplateController::class, 'export');
Route::ajax("templates_import", TemplateController::class, 'import');

// dashboard
Route::ajax("dashboard_usages", UsageController::class);
Route::ajax("dashboard_latest_publications", DashboardController::class, 'latestPublications');
Route::ajax("dashboard_next_publications", DashboardController::class, 'nextPublications');
Route::ajax("dashboard_global_metrics", DashboardController::class, 'globalMetrics');

// help center
Route::ajax("help_center_index", HelpCenterController::class);

// pricing plans
Route::ajax("pricing_plans_index", PricingPlanController::class);

// image generator
Route::ajax("image_generator_generate", ImageGeneratorController::class, 'generate');
Route::ajax("image_generator_generate_description", ImageGeneratorController::class, 'generateDescription');
Route::ajax("image_generator_save", ImageGeneratorController::class, 'save');

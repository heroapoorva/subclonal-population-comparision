$(document).ready(function() { 
    $('#run_pipeline').on('click', function() { 
        var value = getData();
        $.ajax({
            type: 'POST',
            url: "/",
            data: JSON.stringify(value),
            contentType: 'application/json',
            success: function(data) {
                window.location = data;
            }
        });
    })
})

function getData() {
    var yaml = getCcfData()
    yaml.ccf_algorithm = getCcf()
    yaml.input_dir = "../data/Simulations_August"
    yaml.output_dir = "./out"
    yaml.nmf_params = {"num_topics": parseFloat($("#nmf_topics").val())}
    yaml.lda_params = {"num_topics": parseFloat($("#lda_topics").val())}
    yaml.classifier_params = {"num_classes": parseFloat($("#classifier_classes").val())}
    yaml.use_intermediate = $('#inter_data').prop('checked')
    console.log(yaml.use_intermediate)
    yaml.use_classified = $('#classified_data').prop('checked')
    return yaml
} 

function getCcfData() {
    var ccf = {
        "pyclone_params": {
            "base_measure_params": {
                "alpha": parseFloat($("#aplha").val()),
                "beta": parseFloat($("#beta").val())
            },
            "beta_binomial_precision_params": {
                "prior": {
                    "rate": parseFloat($("#pr_rate").val()),
                    "shape": parseFloat($("#pr_shape").val())
                },
                "proposal":
                {
                    "precision": parseFloat($("#prop_prec").val())
                },
                "value": parseFloat($("#value").val())
            },
            "concentration": {
                "prior": {
                    "rate": parseFloat($("#con_pr_rate").val()),
                    "shape": parseFloat($("#con_pr_shape").val())
                },
                "value": parseFloat($("#con_val").val())
            },
            "density": pycloneDensity(),
            "num_iters": parseFloat($("#iters").val()),
            "samples": {
                "SAMPLE_NAME": {
                    "error_rate": 0.001,
                    "mutations_file": "MUTATIONS_FILE",
                    "tumour_content": {
                        "value": "TUMOUR_PURITY"
                    }
                }
            },
            "trace_dir": "trace",
            "working_dir": "WORKING_DIR"
        },
        "phylowgs_params": {
            "cnv_format": phylowgs_cnv(),
            "vcf_format": phylowgs_vcf(),
            "BURNIN_SAMPLES": parseFloat($("#burnin").val()),
            "MCMC_SAMPLES": parseFloat($("#mcmc").val()),
            "MH_ITERATIONS": parseFloat($("#mh_iters").val()),
        },
        "ccube_params": {
            "numOfClusterPool": parseFloat($("#cluster").val()),
            "maxSNV": parseFloat($("#maxSNV").val())
        }
    }
    return ccf
}

function phylowgs_cnv(){
    if ($("#cnv_format").val() == "Battenberg"){
        return "battenberg"
    }
}

function phylowgs_vcf(){
    if ($("#vcf_format").val() == "PCAWG Consensus"){
        return "pcawg_consensus"
    }
}

function pycloneDensity() {
    if ($("#desnity").val() == "PyClone Beta Binomial") {
        return "pyclone_beta_binomial"
    } else {
        return "pyclone_binomial"
    }
}

function getCcf(){
    if ($('#pyclone_args').hasClass('active')) { return "pyclone"}
    if ($('#phylowgs_args').hasClass('active')) { return "phylowgs"}   
    if ($('#ccube_args').hasClass('active')) { return "ccube"}
}